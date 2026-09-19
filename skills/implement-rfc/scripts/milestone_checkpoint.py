#!/usr/bin/env python3
"""Observational primary-session plan checkpoints; no synthetic child dispatch."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess

import execution_strategy as strategies
import milestone_plan as plans
import project_config
from milestone_continuation import binding_errors, completion_errors, bound_action
from milestone_state import repository_state

SCHEMA = 'implement-rfc.milestone-checkpoint.v1'


def bind(root, target, selection, run_id, segment_id, mandate_revision, milestone=None, accepted=()):
    context = project_config.resolve_context(repo_root=root)
    if context.mode == 'personal':
        import personal_lanes
        if personal_lanes._read(context.source_root) is not None:
            personal_lanes.validate_pair(context)
    strategies.validate_selection(selection)
    if not selection['configuration_complete']:
        raise ValueError('strategy requires exact routing before binding work')
    found = plans.discover(context.workflow_root, context.config, targets=[target])
    if found['state'] != 'found':
        raise ValueError('resolve/adopt the authored plan before binding')
    path = Path(found['path'])
    plan = plans.load_plan(path)
    eligible = [item for item in plan['milestones'] if item['id'] not in accepted and set(item['depends_on']) <= set(accepted)]
    selected = next((item for item in eligible if item['id'] == milestone), None) if milestone else next(iter(eligible), None)
    if selected is None:
        raise ValueError('milestone is unknown, accepted or has unmet prerequisites')
    binding = plans.resolve_binding(context.source_root, path.relative_to(context.workflow_root).as_posix(), selected['id'])
    if binding_errors(binding):
        raise ValueError('; '.join(binding_errors(binding)))
    if any(not isinstance(v, str) or not v.strip() for v in (run_id, segment_id, mandate_revision)):
        raise ValueError('run, segment and mandate identity are required')
    return dict(schema=SCHEMA, run_id=run_id, segment_id=segment_id, mandate_revision=mandate_revision,
                selection=selection, target=target, binding=binding,
                target_milestones=[item['id'] for item in plan['milestones']], repository_state=repository_state(context))


def check(root, checkpoint, observation, execution, accepted=()):
    def result(action, detail):
        return dict(action=action, detail=detail, engineering_acceptance='not-evaluated')
    fields = {'schema', 'run_id', 'segment_id', 'mandate_revision', 'selection', 'target',
              'binding', 'target_milestones', 'repository_state'}
    if not isinstance(checkpoint, dict) or set(checkpoint) != fields or checkpoint.get('schema') != SCHEMA:
        raise ValueError('invalid checkpoint')
    strategies.validate_selection(checkpoint['selection'])
    context = project_config.resolve_context(repo_root=root)
    if context.mode == 'personal':
        import personal_lanes
        if personal_lanes._read(context.source_root) is not None:
            personal_lanes.validate_pair(context)
    current_state = repository_state(context)
    prior = checkpoint['repository_state']
    if not isinstance(prior, dict) or prior.keys() != current_state.keys():
        raise ValueError('invalid repository binding')
    for key, value in current_state.items():
        if not key.endswith('_revision') and prior[key] != value:
            return result('reconcile', 'source/tracker root, worktree or branch changed')
    required = {'run_id', 'segment_id', 'mandate_revision', 'selection', 'milestone', 'binding',
                'disposition', 'candidate_revision', 'handoff_ref', 'required_pending', 'evidence_refs',
                'acceptance_records', 'continuation', 'ownership'}
    if not isinstance(observation, dict) or set(observation) != required:
        raise ValueError('invalid observation fields')
    if any(observation[key] != checkpoint[key] for key in ('run_id', 'segment_id', 'mandate_revision', 'selection')):
        return result('ignore-stale', 'observation belongs to another run, segment, mandate or strategy')
    if observation['disposition'] not in ('milestone-complete', 'pack-complete', 'continue-milestone', 'human-pending', 'blocked', 'cancelled'):
        raise ValueError('invalid primary disposition')
    for key in ('required_pending', 'evidence_refs'):
        if not isinstance(observation[key], list) or any(not isinstance(v, str) or not v for v in observation[key]):
            raise ValueError('invalid pending/evidence references')
    errors = completion_errors(observation)
    if errors:
        return result('reconcile', '; '.join(errors))
    if observation['disposition'] == 'cancelled':
        return result('stop', 'preserve current effects; cancellation grants no further work')
    if execution == 'active':
        return result('wait', 'task-owned writers or commands remain active')
    if execution != 'quiescent' or observation['ownership'] != 'quiescent':
        return result('reconcile', 'writer/command effects are uncertain')
    if observation['candidate_revision'] != current_state['source_revision']:
        return result('reconcile', 'candidate revision is not the current source revision')
    for prefix in ('source', 'workflow'):
        completed = subprocess.run(['git', '-C', current_state[prefix + '_root'], 'merge-base', '--is-ancestor',
                                    prior[prefix + '_revision'], current_state[prefix + '_revision']],
                                   env=project_config.git_environment(), capture_output=True)
        if completed.returncode:
            return result('reconcile', 'repository history no longer descends from checkpoint')
    binding = checkpoint['binding']
    current = plans.resolve_binding(context.source_root, binding['plan_path'], binding['milestone_id'])
    plan = plans.load_plan(plans.safe_path(context.workflow_root, binding['plan_path']))
    targets = [item['id'] for item in plan['milestones']]
    if set(accepted) - set(targets):
        raise ValueError('unknown accepted milestone')
    eligible = [item['id'] for item in plan['milestones'] if item['id'] not in accepted and set(item['depends_on']) <= set(accepted)]
    next_id = observation['continuation']['next_milestone']
    if next_id and next_id != binding['milestone_id'] and next_id not in eligible:
        # The current milestone may supply the prerequisite only on a complete observation.
        after = set(accepted) | ({binding['milestone_id']} if observation['disposition'] == 'milestone-complete' else set())
        if not any(item['id'] == next_id and set(item['depends_on']) <= after for item in plan['milestones']):
            return result('reconcile', 'next milestone is not dependency-eligible')
    action, detail = bound_action(observation, checkpoint, current, accepted, targets, eligible)
    return result(action, detail)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['bind', 'check'])
    parser.add_argument('--repo-root', type=Path, required=True)
    parser.add_argument('--target')
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--run-id')
    parser.add_argument('--segment-id')
    parser.add_argument('--mandate-revision')
    parser.add_argument('--milestone')
    parser.add_argument('--accepted-milestone', action='append', default=[])
    parser.add_argument('--checkpoint', type=Path)
    parser.add_argument('--observation', type=Path)
    parser.add_argument('--execution', choices=['quiescent', 'active', 'unknown'], default='unknown')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        if args.operation == 'bind':
            value = bind(args.repo_root, args.target, strategies.read_json(args.selection), args.run_id,
                         args.segment_id, args.mandate_revision, args.milestone, args.accepted_milestone)
        else:
            value = check(args.repo_root, strategies.read_json(args.checkpoint), strategies.read_json(args.observation),
                          args.execution, args.accepted_milestone)
        print(json.dumps(value) if args.json else value.get('detail', 'Primary milestone binding computed'))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(json.dumps({'state': 'invalid', 'detail': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
