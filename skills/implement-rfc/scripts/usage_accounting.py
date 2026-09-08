"""Offline conservative reconciliation. Price equivalents are never subscription debits."""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
import json
import sqlite3
import tempfile
from pathlib import Path
from usage_capture import DiskMap, dt, digest, tokens

SCHEMAS={'rfc-usage-evidence.v1','rfc-usage-evidence.v2'}
KEYS=('input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens')


def identity(event):
    return [event.get(k) for k in ('provider','provider_account_alias','device_alias','session')]


def ledger_row(event,classification,counts=None,anomalies=(),basis=None):
    return {**{k:event.get(k) for k in ('project','provider','provider_account_alias','device_alias','session','turn_id','response_id','task_id','attempt_id','model','effort','service_tier','timestamp')},
            'classification':classification,'tokens':counts,'anomalies':list(anomalies),'basis':basis,
            'route_evidence':'configuration' if event.get('context_is_configuration_not_response') else 'runtime_response',
            'subscription_spend':None}


def codex_counts(value):
    picked={k:value[k] for k in KEYS if type(value.get(k)) is int and value[k]>=0}
    if 'input_tokens' not in picked or 'output_tokens' not in picked:
        return None
    if picked.get('cached_input_tokens',0)>picked['input_tokens'] or picked.get('reasoning_output_tokens',0)>picked['output_tokens']:
        return None
    # Subsets never increase their parent totals. Unknown cache partition stays null.
    picked['uncached_input_tokens']=picked['input_tokens']-picked['cached_input_tokens'] if 'cached_input_tokens' in picked else None
    return picked


def reconcile(events,baselines=(),schema='rfc-usage-evidence.v2'):
    if schema not in SCHEMAS:raise ValueError('Unsupported capture schema')
    # Sort bounded input records on disk; transcript traversal order is not time order.
    with tempfile.TemporaryDirectory(prefix='rfc-reconcile-') as tmp:
        db=sqlite3.connect(str(Path(tmp)/'events.sqlite'))
        db.execute('PRAGMA cache_size=-2048')
        db.execute('CREATE TABLE events (id TEXT PRIMARY KEY, timestamp TEXT, body TEXT)')
        previous=DiskMap();claude=DiskMap()
        try:
            for event in baselines:
                if event.get('cumulative') and event.get('session') and event.get('ownership') not in ('uncertain_fork_or_child','native_session_project_conflict'):
                    previous[identity(event)]={'counters':tokens(event['cumulative']),'epoch':0,'timestamp':event.get('timestamp')}
            for event in events:
                if not isinstance(event,dict):raise ValueError('Invalid event record')
                when=dt(event.get('timestamp'))
                if when is None:
                    yield ledger_row(event,'unknown',anomalies=['invalid_timestamp']);continue
                encoded=json.dumps(event,sort_keys=True)
                if len(encoded)>1024*1024:raise ValueError('Event exceeds reconciliation bound')
                # Copies with the same source identity deduplicate; conflicting IDs refuse.
                eid=event.get('event_id') or digest(event)
                existing=db.execute('SELECT body FROM events WHERE id=?',(eid,)).fetchone()
                if existing:
                    if json.loads(existing[0])!=event:raise ValueError('Conflicting duplicate event identity')
                    continue
                db.execute('INSERT INTO events VALUES (?,?,?)',(eid,when.isoformat(),encoded))
            for body, in db.execute('SELECT body FROM events ORDER BY timestamp,id'):
                event=json.loads(body);provider=event.get('provider');kind=event.get('kind')
                if provider=='claude' and kind=='assistant_record':
                    if event.get('synthetic_or_api_error'):
                        yield ledger_row(event,'synthetic_error',anomalies=['not_serving_model_work']);continue
                    response=event.get('response_id')
                    if not response:
                        yield ledger_row(event,'unknown',anomalies=['response_identity_missing']);continue
                    key=identity(event)+[response]
                    group=claude.get(key)
                    usage=tokens(event.get('usage'))
                    if group is None:
                        group={'event':event,'usage':usage,'conflicts':[],'output_complete':bool(event.get('stop_reason'))}
                    else:
                        for name,value in usage.items():
                            old=group['usage'].get(name)
                            if name=='output_tokens' and type(value) is int:
                                group['usage'][name]=max(old or 0,value)
                            elif old is not None and old!=value:
                                if name not in group['conflicts']:group['conflicts'].append(name)
                            else:group['usage'][name]=value
                        if event.get('stop_reason'):
                            group['output_complete']=True
                            group['event']=event
                    claude[key]=group
                elif provider=='codex' and kind=='token_observation':
                    key=identity(event);current=tokens(event.get('cumulative'));prior=previous.get(key)
                    if event.get('ownership') in ('uncertain_fork_or_child','native_session_project_conflict'):
                        yield ledger_row(event,'ownership_uncertain',anomalies=['inherited_or_conflicting_ownership']);continue
                    if not current:
                        yield ledger_row(event,'unknown',anomalies=['cumulative_series_missing']);continue
                    if prior is None:
                        previous[key]={'counters':current,'epoch':0,'timestamp':event['timestamp']}
                        yield ledger_row(event,'unknown',anomalies=['pre_window_baseline_missing']);continue
                    before=prior['counters'];epoch=prior['epoch']
                    if current==before:continue
                    delta={k:current[k]-before[k] for k in KEYS if type(current.get(k)) is int and type(before.get(k)) is int}
                    previous[key]={'counters':current,'epoch':epoch,'timestamp':event['timestamp']}
                    if any(v<0 for v in delta.values()):
                        previous[key]={'counters':current,'epoch':epoch+1,'timestamp':event['timestamp']}
                        yield {**ledger_row(event,'unknown',anomalies=['counter_decrease_or_reset']), 'usage_epoch':epoch+1};continue
                    counts=codex_counts(delta)
                    if counts is None:
                        yield ledger_row(event,'unknown',anomalies=['missing_or_conflicting_counter_categories']);continue
                    last=tokens(event.get('last'))
                    corroborated=bool(last) and all(last.get(k)==v for k,v in delta.items())
                    classification='request_reconciled' if corroborated and event.get('response_id') else 'aggregate_only'
                    yield {**ledger_row(event,classification,counts,basis='monotonic_cumulative_delta'), 'usage_epoch':epoch,
                           'last_corrobates_delta':corroborated}
                # Harness footprints, final inclusive aggregates and compaction are never additive requests.
            for group in claude.values():
                event=group['event'];usage=group['usage'];anomalies=[]
                if group['conflicts']:anomalies.append('conflicting_request_counters')
                if not group['output_complete']:anomalies.append('output_incomplete')
                if 'input_tokens' not in usage:anomalies.append('input_missing')
                if not group['output_complete'] or 'output_tokens' not in usage:output=None
                else:output=usage['output_tokens']
                cached=usage.get('cache_read_input_tokens',0)
                created=usage.get('cache_creation_input_tokens')
                if created is None:
                    details=usage.get('cache_creation',{})
                    created=sum(details.get(k,0) for k in ('ephemeral_5m_input_tokens','ephemeral_1h_input_tokens'))
                uncached=usage.get('input_tokens')
                counts={'input_tokens':uncached+cached+created if uncached is not None else None,
                        'uncached_input_tokens':uncached,'cached_input_tokens':cached,'cache_creation_input_tokens':created,'output_tokens':output}
                yield ledger_row(event,'request_reconciled' if not anomalies else 'unknown',counts,anomalies,basis='native_response_id_fragments')
        finally:
            previous.close();claude.close();db.close()


def estimate(row,rate_card,mode='historical-rate estimate'):
    if mode not in ('historical-rate estimate','current-rate counterfactual'):raise ValueError('Unknown rate mode')
    unknown={'amount':None,'mode':mode,'meaning':'price_equivalent_not_subscription_spend'}
    if row['classification'] not in ('request_reconciled','aggregate_only') or row.get('route_evidence')!='runtime_response' or row.get('model') in (None,'unknown','<synthetic>'):return unknown
    moment=dt(row.get('timestamp'))
    for rate in rate_card:
        if any(rate.get(k)!=row.get(k) for k in ('provider','model','service_tier')) or not row.get('service_tier'):continue
        start,end=dt(rate.get('effective_from')),dt(rate.get('effective_until'))
        if not start or not end or not rate.get('source'):continue
        if mode=='historical-rate estimate' and not (moment and start<=moment<end):continue
        counts=row.get('tokens') or {};cost=Decimal(0)
        try:
            for name in ('uncached_input_tokens','cached_input_tokens','cache_creation_input_tokens','output_tokens'):
                count=counts.get(name,0 if name=='cache_creation_input_tokens' else None)
                if count is None:return unknown
                price=Decimal(str(rate['per_million'][name]))
                if not price.is_finite() or price<0:return unknown
                cost+=Decimal(count)*price/Decimal(1000000)
            multiplier=Decimal(str(rate['tier_multiplier']))
            if not multiplier.is_finite() or multiplier<0:return unknown
            return {'amount':str(cost*multiplier),'unit':rate['unit'],'mode':mode,'source':rate['source'],
                    'meaning':'price_equivalent_not_subscription_spend'}
        except (KeyError,InvalidOperation,TypeError):return unknown
    return unknown
