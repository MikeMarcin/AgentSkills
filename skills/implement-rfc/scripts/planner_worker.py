#!/usr/bin/env python3
"""Check supplied strict-recipe observations; no dispatch or acceptance authority."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import execution_strategy as strategy

SCHEMA = 'implement-rfc.planner-worker-observation.v1'


def check(selection, record):
    strategy.validate_selection(selection)
    if selection['topology_id'] != 'planner-worker' or not selection['configuration_complete']:
        raise ValueError('strict recipe requires exact primary and worker routes')
    if (not isinstance(record, dict) or set(record) != {'schema', 'coverage', 'events'}
            or record['schema'] != SCHEMA or record['coverage'] not in ('complete', 'partial')):
        raise ValueError('invalid strict recipe observation')
    events = record['events']
    if not isinstance(events, list) or len(events) > 10000:
        raise ValueError('bounded event list required')
    active = set()
    workers = set()
    deviations = set()
    unknown = []
    primary_observed = False
    fields = {'kind', 'actor', 'evidence_ref'}
    kinds = {'start', 'stop', 'feedback', 'product-edit', 'bookkeeping', 'delegate', 'route'}
    for event in events:
        if (not isinstance(event, dict) or not fields <= event.keys()
                or event.keys() - fields - {'route', 'role'} or event['kind'] not in kinds
                or any(not isinstance(event[k], str) or not event[k].strip() for k in fields)):
            raise ValueError('events require kind, actor and evidence reference')
        actor, kind = event['actor'], event['kind']
        if kind == 'start' and event.get('role') != ('planner' if actor == 'planner' else 'worker'):
            deviations.add('unexpected_child_or_role')
        if kind != 'start' and 'role' in event:
            raise ValueError('role belongs to start observations')
        if 'route' in event and kind not in ('start', 'route'):
            raise ValueError('routes belong to start or route observations')
        if kind in ('start', 'route'):
            route = event.get('route')
            if route is None:
                unknown.append(event['evidence_ref'] + ': serving route unknown')
            else:
                strategy.routes({'observed': route})
                expected = selection['routing']['primary' if actor == 'planner' else 'worker']
                if route != expected:
                    deviations.add('route_change')
                if actor == 'planner':
                    primary_observed = True
        if kind == 'start':
            if actor == 'planner':
                continue
            if actor in active:
                raise ValueError('duplicate active worker observation')
            active.add(actor)
            workers.add(actor)
            if len(active) > 1:
                deviations.add('multiple_active_workers')
        elif kind == 'stop':
            if actor not in active:
                unknown.append(event['evidence_ref'] + ': stop without observed active worker')
            active.discard(actor)
        elif kind == 'feedback':
            if actor != 'planner':
                deviations.add('worker_owned_decision')
        elif kind == 'product-edit':
            if actor == 'planner':
                deviations.add('planner_takeover')
            elif actor not in active:
                unknown.append(event['evidence_ref'] + ': edit without observed active worker')
        elif kind == 'bookkeeping' and actor != 'planner':
            deviations.add('worker_owned_bookkeeping')
        elif kind == 'delegate' and actor != 'planner':
            deviations.add('recursive_delegation')
    if not workers:
        unknown.append('no worker execution observed')
    if not primary_observed:
        unknown.append('primary serving route unknown')
    if deviations:
        state = 'deviated'
    elif unknown or record['coverage'] != 'complete' or active:
        state = 'incomplete'
    else:
        state = 'consistent'
    return dict(state=state, deviations=sorted(deviations), unknown=unknown, active_workers=sorted(active),
                observation_coverage=record['coverage'], host_load='not_verified',
                limitation='Supplied observations do not certify enforcement or product acceptance.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['check'])
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--record', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = check(strategy.read_json(args.selection), strategy.read_json(args.record))
        print(json.dumps(result))
        return 0 if result['state'] == 'consistent' else 1
    except (ValueError, OSError, TypeError) as exc:
        print(json.dumps(dict(state='invalid', detail=str(exc))))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
