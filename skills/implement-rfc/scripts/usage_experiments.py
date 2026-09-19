"""Versioned multi-arm provenance and conservative accounting over the existing ledger."""
from __future__ import annotations
from collections import defaultdict
from usage_capture import dt
from usage_accounting import codex_counts

SCHEMA = 'implement-rfc.experiment.v2'
COMMON = {'task_reference','source_base','tracker_base','authored_plan_reference','skill_revision',
          'acceptance_gate_reference','environment_reference','isolation_reference','budget_and_repair_policy_reference'}


def text(value):
    return isinstance(value,str) and bool(value.strip()) and '<' not in value


def validate(value):
    required={'schema','status','study_id','comparison_kind','common_inputs','arms','judges','order'}
    optional={'available_additional_arms','measurement','notes','inclusive_observations'}
    if not isinstance(value,dict) or not required <= value.keys() or value.keys()-required-optional or value.get('schema')!=SCHEMA:
        raise ValueError('invalid multi-arm experiment v2')
    if value['status'] not in ('draft_not_runnable','frozen','completed') or not text(value['study_id']):
        raise ValueError('explicit study identity and status required')
    if value['comparison_kind']!='practical_strategy_comparison_not_topology_only':
        raise ValueError('v2 compares practical strategies, not a one-factor causal effect')
    common=value['common_inputs']
    if not isinstance(common,dict) or set(common)!=COMMON:
        raise ValueError('common frozen input references required')
    if not isinstance(value['arms'],list) or not 1<=len(value['arms'])<=32:
        raise ValueError('select a bounded nonempty list of arms')
    ids=set()
    arm_fields={'arm_id','strategy','topology_id','recipe_revision','requested_routing','child_route_ownership',
                'effective_configuration_reference','observed_serving_reference','source_worktree','tracker_worktree'}
    missing=[]
    for arm in value['arms']:
        if not isinstance(arm,dict) or set(arm)!=arm_fields or any(not text(arm.get(k)) for k in ('arm_id','strategy','topology_id')):
            raise ValueError('invalid selected arm')
        if arm['arm_id'] in ids: raise ValueError('duplicate arm identity')
        ids.add(arm['arm_id'])
        if arm['child_route_ownership'] not in ('disabled','native_system','recipe'):
            raise ValueError('explicit child-route ownership required')
        routes=arm['requested_routing']
        if not isinstance(routes,dict): raise ValueError('requested routing must be a map')
        for route in routes.values():
            if not isinstance(route,dict) or set(route)!= {'provider','model','effort'}:
                raise ValueError('route slots need provider/model/effort')
            if any(not text(item) for item in route.values()): missing.append(arm['arm_id']+': exact route')
        for key in ('recipe_revision','effective_configuration_reference','source_worktree'):
            if not text(arm[key]): missing.append(arm['arm_id']+': '+key)
        if not routes: missing.append(arm['arm_id']+': requested routing snapshot')
    for key in COMMON:
        # Project-mode tracker identity can explicitly be the same committed source base.
        if not text(common[key]): missing.append(key)
    judges=value['judges']
    if not isinstance(judges,list) or not 1<=len(judges)<=8: raise ValueError('bounded judge list required')
    for judge in judges:
        if not isinstance(judge,dict) or set(judge)!= {'family','exact_model','effort'} or not text(judge['family']):
            raise ValueError('invalid judge route')
        if not text(judge['exact_model']) or not text(judge['effort']): missing.append('judge exact route')
    if len({judge['family'] for judge in judges}) != len(judges):
        raise ValueError('duplicate judge identity')
    order=value['order']
    if not isinstance(order,dict) or set(order)!= {'implementation','candidate_labels_private','judge_orders'}:
        raise ValueError('explicit order and blinding policy required')
    sequence=order['implementation']
    if sequence is None: missing.append('implementation order')
    elif not isinstance(sequence,list) or len(sequence)!=len(ids) or any(not isinstance(v,str) for v in sequence) or set(sequence)!=ids:
        raise ValueError('implementation order must contain each selected arm once')
    if order['candidate_labels_private'] is not True: raise ValueError('quality views need private treatment labels')
    if not isinstance(order['judge_orders'],dict) or not order['judge_orders']: missing.append('judge presentation orders')
    elif set(order['judge_orders'])!={j['family'] for j in judges}:
        raise ValueError('presentation order required for every judge')
    else:
        labels = None
        for sequence in order['judge_orders'].values():
            if not isinstance(sequence,list) or len(sequence)!=len(ids) or any(not text(v) for v in sequence) or len(set(sequence))!=len(ids):
                raise ValueError('each judge needs one neutral label per candidate')
            if labels is not None and labels != set(sequence):
                raise ValueError('judges must see the same candidate label set')
            labels = set(sequence)
    observations=value.get('inclusive_observations',[])
    if not isinstance(observations,list) or len(observations)>1000: raise ValueError('bounded aggregate observations required')
    seen=set()
    fields={'observation_id','arm_id','attempt_id','provider','provider_account_alias','device_alias',
            'since','until','usage','semantics','coverage','evidence_ref','phase'}
    for observation in observations:
        if not isinstance(observation,dict) or set(observation)!=fields:
            raise ValueError('inclusive observations require exact identity, interval, semantics and evidence')
        if any(not text(observation[k]) for k in fields-{'usage'}): raise ValueError('incomplete aggregate identity')
        if observation['arm_id'] not in ids or observation['observation_id'] in seen:
            raise ValueError('unknown arm or duplicate aggregate')
        seen.add(observation['observation_id'])
        if observation['phase'] not in ('initial','repair'): raise ValueError('aggregate phase required')
        if observation['semantics'] not in ('inclusive','unknown') or observation['coverage'] not in ('whole_attempt','partial'):
            raise ValueError('explicit aggregate semantics required')
        if not dt(observation['since']) or not dt(observation['until']) or dt(observation['since'])>=dt(observation['until']):
            raise ValueError('aggregate interval required')
        if codex_counts(observation['usage']) is None: raise ValueError('invalid normalized aggregate counters')
    if value['status']!='draft_not_runnable' and missing:
        raise ValueError('unresolved frozen inputs: '+', '.join(missing))
    if value['status']=='draft_not_runnable' and observations:
        raise ValueError('draft studies cannot contain run observations')
    return sorted(set(missing))


def assignment_for(row, assignments):
    moment=dt(row.get('timestamp'))
    if moment is None:return None
    matches=[a for a in assignments if a['session']==row.get('session')
             and dt(a['since'])<=moment<dt(a['until'])
             and (not row.get('task_id') or a['task_id']==row['task_id'])
             and (not row.get('attempt_id') or a['attempt_id']==row['attempt_id'])]
    if row.get('classification') == 'aggregate_only':
        since, until = dt(row.get('usage_since')), dt(row.get('usage_until'))
        if since is None or until is None or since >= until:
            return None
        matches = [a for a in matches if dt(a['since']) <= since and until < dt(a['until'])]
    return matches[0] if len(matches)==1 else None


def summarize(experiment, outcomes, rows):
    """One combined reconciled stream; inclusive observations replace covered components."""
    validate(experiment)
    arms={a['arm_id']:a for a in experiment['arms']}
    assignments=outcomes.assignments
    buckets=defaultdict(lambda: {'input_tokens':0,'output_tokens':0,'unknown_rows':0,'rows':0,'since':None,'until':None,
                                 'coverage':set(),'route_ownership':set(),'deviations':set(),'phases':set()})
    unassigned=0
    observed_assignments = set()
    for assignment in assignments:
        if assignment.get('study_id')!=experiment['study_id']:continue
        arm=assignment.get('arm_id')
        cost=assignment.get('cost_bucket','arm')
        if cost not in ('arm','shared_review','setup'):raise ValueError('invalid study cost bucket')
        if cost=='arm' and arm not in arms:raise ValueError('assignment names unknown arm')
        if assignment.get('coverage') not in ('complete','partial','unavailable'):raise ValueError('explicit attempt coverage required')
        if assignment.get('route_ownership','unknown') not in ('system','custom','unknown'):raise ValueError('invalid route ownership')
        if assignment.get('phase') not in ('initial','repair'):raise ValueError('explicit initial/repair phase required')
        if not isinstance(assignment.get('deviations',[]),list) or any(not text(v) for v in assignment.get('deviations',[])):
            raise ValueError('invalid deviation observations')
        if cost=='arm' and any(assignment.get(k)!=arms[arm][k] for k in ('strategy','topology_id','recipe_revision')):
            raise ValueError('declared assignment strategy differs from frozen arm; record actual drift as deviations')
    for row in rows:
        assignment=assignment_for(row,assignments)
        if assignment is None or assignment.get('study_id')!=experiment['study_id']:
            if row['classification']!='alternate_observation' or row['anomalies']:unassigned+=1
            continue
        observed_assignments.add(id(assignment))
        cost=assignment.get('cost_bucket','arm')
        arm=assignment.get('arm_id') if cost=='arm' else None
        key=(cost,arm,assignment['attempt_id'],row.get('provider'),row.get('provider_account_alias'),row.get('device_alias'))
        bucket=buckets[key]
        bucket['coverage'].add(assignment['coverage']);bucket['phases'].add(assignment['phase'])
        bucket['route_ownership'].add(assignment.get('route_ownership','unknown'))
        bucket['deviations'].update(assignment.get('deviations',[]))
        if row['classification']=='alternate_observation' and not row['anomalies']:continue
        bucket['rows']+=1
        since,until=dt(assignment['since']),dt(assignment['until'])
        bucket['since']=min(bucket['since'],since) if bucket['since'] else since
        bucket['until']=max(bucket['until'],until) if bucket['until'] else until
        counts=row.get('tokens') or {}
        if row['classification'] in ('request_reconciled','aggregate_only') and all(type(counts.get(k)) is int for k in ('input_tokens','output_tokens')):
            for k in ('input_tokens','output_tokens'):bucket[k]+=counts[k]
        else:bucket['unknown_rows']+=1
    aggregates=defaultdict(list)
    for item in experiment.get('inclusive_observations',[]):
        key=('arm',item['arm_id'],item['attempt_id'],item['provider'],item['provider_account_alias'],item['device_alias'])
        aggregates[key].append(item)
        buckets[key]['phases'].add(item['phase'])  # Inclusive totals can lack visible descendants.
    for assignment in assignments:
        if assignment.get('study_id')!=experiment['study_id']:continue
        if id(assignment) in observed_assignments:continue
        cost=assignment.get('cost_bucket','arm');arm=assignment.get('arm_id') if cost=='arm' else None
        prefix=(cost,arm,assignment['attempt_id'])
        keys = [key for key in buckets if key[:3] == prefix]
        if not keys:
            keys = [(*prefix, 'unknown', 'unknown', 'unknown')]
        for key in keys:
            bucket = buckets[key]
            bucket['unknown_rows'] += 1
            bucket['coverage'].add('unavailable')
            bucket['phases'].add(assignment['phase'])
            bucket['route_ownership'].add(assignment.get('route_ownership', 'unknown'))
            bucket['deviations'].update(assignment.get('deviations', []))
            since, until = dt(assignment['since']), dt(assignment['until'])
            bucket['since'] = min(bucket['since'], since) if bucket['since'] else since
            bucket['until'] = max(bucket['until'], until) if bucket['until'] else until
    results=[]
    for key,bucket in buckets.items():
        observed={k:bucket[k] for k in ('input_tokens','output_tokens')}
        exact=bool(bucket['rows']) and bucket['coverage']=={'complete'} and bucket['unknown_rows']==0
        selected=None;notes=[]
        candidates=[v for v in aggregates[key] if v['semantics']=='inclusive' and v['coverage']=='whole_attempt']
        if len(candidates)==1:
            aggregate=candidates[0];counts=codex_counts(aggregate['usage'])
            if bucket['since'] is None or (dt(aggregate['since'])<=bucket['since'] and bucket['until']<=dt(aggregate['until'])):
                if all(counts[k]>=observed[k] for k in observed):
                    selected=aggregate['observation_id'];observed={k:counts[k] for k in observed};exact=True
                else:notes.append('inclusive_total_smaller_than_visible_components');exact=False
            else:notes.append('inclusive_interval_does_not_cover_assigned_work');exact=False
        elif len(candidates)>1:notes.append('overlapping_or_multiple_inclusive_totals');exact=False
        if aggregates[key] and selected is None:
            notes.append('aggregate_observations_retained_separately');exact=False
        if len(bucket['phases'])>1:notes.append('attempt_mixes_initial_and_repair');exact=False
        results.append(dict(cost_bucket=key[0],arm_id=key[1],attempt_id=key[2],provider=key[3],
            provider_account_alias=key[4],device_alias=key[5],phase=next(iter(bucket['phases'])) if len(bucket['phases'])==1 else 'unknown',
            observed_tokens=sum(observed.values()),exact_tokens=sum(observed.values()) if exact else None,
            observed_components_tokens=bucket['input_tokens']+bucket['output_tokens'],inclusive_observation=selected,
            aggregate_observations=aggregates[key],unknown_rows=bucket['unknown_rows'],coverage=sorted(bucket['coverage']),
            route_ownership=sorted(bucket['route_ownership']),deviations=sorted(bucket['deviations']),notes=notes))
    return dict(study_id=experiment['study_id'],arms=[dict(arm_id=key,strategy=arm['strategy'],
        topology_id=arm['topology_id'],requested_routing=arm['requested_routing'],
        observed_serving_reference=arm['observed_serving_reference'],
        attempts=[row for row in results if row['arm_id']==key]) for key,arm in arms.items()],
        shared_costs=[row for row in results if row['cost_bucket']!='arm'],unassigned_rows=unassigned,
        production_deliveries=0,accepted_alternatives=sum(1 for task,data in outcomes.tasks.items() if data['accepted'] and any(a['task_id']==task and a.get('arm_id') in arms and a.get('study_id')==experiment['study_id'] for a in assignments)),
        total_observed_tokens=sum(row['observed_tokens'] for row in results),
        total_exact_tokens=sum(row['exact_tokens'] for row in results) if results and not unassigned and all(any(row['arm_id']==arm for row in results) for arm in arms) and all(row['exact_tokens'] is not None for row in results) else None,
        limitation='Quality, adherence, coverage and economics are separate. Unknown is not zero; totals are tokens, not subscription charges. Trial alternatives are not production deliveries.')
