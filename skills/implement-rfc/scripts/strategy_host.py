#!/usr/bin/env python3
"""Render scoped settings to stdout and inspect supplied host inputs; never apply or launch."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import tomllib
import execution_strategy as strategy

CHILD_SLOTS = {'planner-worker': 'worker', 'coordinator-implementer': 'implementer'}


def render(selection):
    strategy.validate_selection(selection)
    route = selection['routing'].get('primary')
    if not route or route['provider'] != 'codex':
        raise ValueError('scoped Codex settings require an exact primary Codex route')
    child_slot = CHILD_SLOTS.get(selection['topology_id'])
    if child_slot and not selection['configuration_complete']:
        raise ValueError('recipe requires exact primary and ' + child_slot + ' routes')
    if selection['delegation'] not in ('none', 'system') and not child_slot:
        raise ValueError('recipe-specific roles use their own scoped renderer')
    lines = ['# Requested settings only; inspect inherited layers before a new session.',
                      'model = ' + json.dumps(route['model']),
                      'model_reasoning_effort = ' + json.dumps(route['effort']), '', '[agents]',
                      'enabled = ' + ('false' if selection['delegation'] == 'none' else 'true')]
    if child_slot:
        worker = selection['routing'][child_slot]
        lines.extend(['max_concurrent_threads_per_session = 1',
                      'default_subagent_model = ' + json.dumps(worker['model']),
                      'default_subagent_reasoning_effort = ' + json.dumps(worker['effort'])])
    return '\n'.join([*lines, ''])


def render_implementer(selection):
    strategy.validate_selection(selection)
    if selection['topology_id'] != 'coordinator-implementer' or not selection['configuration_complete']:
        raise ValueError('implementer settings require a complete coordinator-implementer selection')
    route = selection['routing']['implementer']
    return render(strategy.resolve('direct', routing={'primary': route}))


def inspect(selection, configs=(), instructions=(), agent_roots=(), *, complete_inputs=False):
    strategy.validate_selection(selection)
    findings = []
    effective = {}
    observed = []
    native = selection['delegation'] == 'system'
    strict = selection['topology_id'] == 'planner-worker'
    child_slot = CHILD_SLOTS.get(selection['topology_id'])
    for path in configs:
        path=Path(path)
        data=tomllib.loads(path.read_text(encoding='utf-8'))
        observed.append(str(path))
        for key in ('model','model_reasoning_effort'):
            if key in data: effective[key]=data[key]
        agents=data.get('agents',{})
        if not isinstance(agents,dict): raise ValueError('invalid agents configuration')
        for key in ('enabled','default_subagent_model','default_subagent_reasoning_effort',
                    'max_concurrent_threads_per_session','max_threads'):
            if key in agents: effective['agents.'+key]=agents[key]
        if (native or strict) and any(isinstance(value,dict) for value in agents.values()):
            findings.append(dict(path=str(path),kind='custom_agent_configuration'))
    for path in instructions:
        path=Path(path);text=path.read_text(encoding='utf-8');observed.append(str(path))
        # These are review signals, not a semantic proof that arbitrary prose is clean.
        if (native or strict) and re.search(r'(?:act as|you are|dispatch|spawn|must use)[^\n]{0,100}(?:coordinator|rfc-integrator|rfc-worker)',text,re.I):
            findings.append(dict(path=str(path),kind='possible_custom_coordination_instruction'))
    for root in agent_roots:
        root=Path(root); observed.append(str(root))
        if not root.is_dir(): raise ValueError('agent discovery root is unavailable')
        for path in sorted(root.iterdir()):
            if (native or strict) and path.suffix in ('.toml','.md'):
                findings.append(dict(path=str(path),kind='custom_agent_definition'))
    if native:
        for key in ('agents.default_subagent_model','agents.default_subagent_reasoning_effort'):
            if key in effective:
                findings.append(dict(kind='inherited_child_route_override',key=key))
    enabled=effective.get('agents.enabled',True)
    if (selection['delegation']=='none' and enabled is not False) or ((native or child_slot) and enabled is not True):
        findings.append(dict(kind='delegation_control_mismatch'))
    if child_slot:
        worker = selection['routing'].get(child_slot, {})
        if (not worker or effective.get('agents.default_subagent_model') != worker.get('model')
                or effective.get('agents.default_subagent_reasoning_effort') != worker.get('effort')):
            findings.append(dict(kind=child_slot + '_route_mismatch_or_unknown'))
        limit = effective.get('agents.max_concurrent_threads_per_session', effective.get('agents.max_threads'))
        if type(limit) is not int or limit != 1:
            findings.append(dict(kind=child_slot + '_concurrency_mismatch_or_unknown'))
    route=selection['routing'].get('primary')
    if route:
        if effective.get('model')!=route['model'] or effective.get('model_reasoning_effort')!=route['effort']:
            findings.append(dict(kind='primary_route_mismatch_or_unknown'))
    if findings:
        state = 'needs_reconciliation'
    elif complete_inputs:
        state = 'configuration_consistent'
    else:
        state = 'incomplete'
    return dict(schema='implement-rfc.strategy-host-inspection.v1',strategy=selection['strategy'],
                requested=selection['routing'],effective_configuration=effective,observed_inputs=observed,
                input_coverage='operator_declared_complete' if complete_inputs else 'partial',
                findings=findings,state=state,
                observed_serving=None,host_load='not_verified',
                limitation='Supplied files and heuristic instruction signals cannot establish actual host loading or absence of undisclosed policy.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation',choices=['render','render-implementer','inspect'])
    parser.add_argument('--selection',type=Path,required=True)
    parser.add_argument('--config',type=Path,action='append',default=[])
    parser.add_argument('--instructions',type=Path,action='append',default=[])
    parser.add_argument('--agent-root',type=Path,action='append',default=[])
    parser.add_argument('--complete-inputs',action='store_true')
    args=parser.parse_args()
    try:
        selection=strategy.read_json(args.selection)
        if args.operation == 'render':
            value = render(selection)
        elif args.operation == 'render-implementer':
            value = render_implementer(selection)
        else:
            value = json.dumps(inspect(selection,args.config,args.instructions,args.agent_root,complete_inputs=args.complete_inputs))
        print(value,end='\n' if args.operation=='inspect' else '')
        return 0
    except (ValueError,OSError,TypeError) as exc:
        print(json.dumps(dict(state='invalid',detail=str(exc))))
        return 2


if __name__=='__main__':
    raise SystemExit(main())
