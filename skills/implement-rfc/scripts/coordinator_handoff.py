"""Pure checks for a native milestone return; never launch or approve work.

The caller supplies native execution observations and retains consumed identities.
The live board and designated integrator still own engineering acceptance.
"""
from __future__ import annotations

from pathlib import PurePosixPath
import re
from milestone_continuation import V2, v2_errors, v2_action, assignment_errors

SCHEMA = "implement-rfc.milestone-return.v1"
IDENTITY = ("run_id", "dispatch_id", "producer_id", "mandate_revision", "milestone")
DISPOSITIONS = {
    "milestone-complete", "continue-milestone", "human-pending", "blocked",
    "cancelled", "pack-complete", "review-request",
}


def validate_return(value: object) -> list[str]:
    """Return structural errors without interpreting evidence as acceptance."""
    required = set(IDENTITY) | {
        "schema", "disposition", "summary", "candidate_revision", "handoff_ref",
        "ownership", "next_objective", "required_pending", "evidence_refs",
    }
    if not isinstance(value, dict) or not required <= value.keys():
        return ["missing required return fields"]
    errors = []
    extension = {"binding", "continuation", "acceptance_records"} if value["schema"] == V2 else set()
    if value.keys() - required - {"review_request"} - extension:
        errors.append("unknown return fields")
    if value["schema"] not in (SCHEMA, V2):
        errors.append("unsupported return schema")
    for key in (*IDENTITY, "summary"):
        if not isinstance(value[key], str) or not value[key].strip():
            errors.append(f"invalid {key}")
    disposition = value["disposition"]
    if not isinstance(disposition, str) or disposition not in DISPOSITIONS:
        errors.append("invalid disposition")
    if value["ownership"] not in ("active", "unknown", "quiescent"):
        errors.append("invalid ownership")
    for key in ("required_pending", "evidence_refs"):
        items = value[key]
        if (not isinstance(items, list)
                or any(not isinstance(item, str) or not item.strip() for item in items)
                or len(set(items)) != len(items)):
            errors.append(f"invalid {key}")
    for key in ("handoff_ref", "next_objective"):
        if value[key] is not None and (not isinstance(value[key], str) or not value[key].strip()):
            errors.append(f"invalid {key}")
    ref = value["handoff_ref"]
    if isinstance(ref, str) and (PurePosixPath(ref).is_absolute() or ".." in PurePosixPath(ref).parts
                                 or "\\" in ref or ":" in ref):
        errors.append("handoff_ref must stay relative to the consumer")
    revision = value["candidate_revision"]
    if revision is not None and (not isinstance(revision, str)
                                or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision) is None):
        errors.append("invalid candidate_revision")
    if disposition == "pack-complete" and (
        value["ownership"] != "quiescent" or value["required_pending"]
        or value["next_objective"] is not None or not value["evidence_refs"]
    ):
        errors.append("pack completion has outstanding obligations or missing evidence")
    if disposition == "milestone-complete" and (
        value["ownership"] != "quiescent" or not value["handoff_ref"] or not value["evidence_refs"]
    ):
        errors.append("milestone completion requires quiescence, handoff and evidence")
    review = value.get("review_request")
    if disposition == "review-request":
        if (not isinstance(review, dict) or set(review) != {"role", "candidate_ref", "assignment"}
                or review.get("role") not in ("rfc-reviewer", "rfc-reviewer-critical")
                or any(not isinstance(review.get(key), str) or not review[key].strip()
                       for key in ("candidate_ref", "assignment"))
                or value["ownership"] != "quiescent"):
            errors.append("invalid review request")
    elif "review_request" in value:
        errors.append("unexpected review request")
    if value["schema"] == V2 and not errors:
        errors.extend(v2_errors(value))
    return errors


def continuation(returned: object, assignment: dict, *, execution: str,
                 consumed=(), cancelled: bool = False, review_relay: bool = False,
                 prior_partial: dict | None = None, current_binding: dict | None = None,
                 accepted_milestones=(), current_target_milestones=None,
                 eligible_milestones=()) -> dict:
    """Suggest a control action from explicit observations, without mutation.

    execution describes the producer AND its owned children/commands, not merely
    the arrival of a message. Unknown ownership requires reconciliation. A caller
    records the returned consumption key only when it actually consumes a result.
    """
    def result(action, reason, key=None):
        return {"action": action, "reason": reason, "consume_key": key,
                "engineering_acceptance": "not-evaluated"}

    if cancelled:
        return result("stop", "current user mandate is cancelled; account for outstanding effects")
    if (not isinstance(consumed, (list, tuple)) or any(not isinstance(item, (list, tuple))
        or len(item) != len(IDENTITY) or any(not isinstance(v, str) for v in item) for item in consumed)):
        return result('reconcile', 'consumed observations must be identity tuple lists')
    if (isinstance(returned, dict) and returned.get("schema") == SCHEMA
            and (assignment.get("binding") is not None or current_binding is not None)):
        return result("reconcile", "legacy return needs scoped plan binding; preserve its native producer")
    errors = validate_return(returned)
    if errors:
        return result("reconcile" if execution == "unknown" else "clarify", "; ".join(errors))
    if returned['schema'] == V2 and assignment_errors(assignment):
        return result('reconcile', '; '.join(assignment_errors(assignment)))
    if returned['schema'] == V2 and (not isinstance(accepted_milestones, (list, tuple))
        or any(not isinstance(item, str) for item in accepted_milestones)
        or set(accepted_milestones) - set(assignment['target_milestones'])):
        return result('reconcile', 'accepted milestone observations differ from the assigned target')
    if any(returned[key] != assignment.get(key) for key in IDENTITY):
        return result("ignore-stale", "result does not match the current native assignment and mandate")
    # A partial invocation may return repeatedly under one dispatch. The native
    # caller supplies a new dispatch identity for an explicitly renewed assignment.
    key = tuple(returned[field] for field in IDENTITY)
    if any(tuple(item) == key for item in consumed):
        return result("ignore-duplicate", "this exact dispatch result was already consumed")
    if returned["disposition"] == "cancelled":
        return result("stop", "producer reports cancellation; reconcile effects before any new mandate", key)
    if execution == "active" or returned["ownership"] == "active":
        return result("wait", "owned execution remains active")
    if execution != "quiescent" or returned["ownership"] != "quiescent":
        return result("reconcile", "native effects and ownership are not established")
    if returned["disposition"] == "review-request" and not review_relay:
        return result("clarify", "native independent-review relay has not been qualified")
    if returned["disposition"] == "continue-milestone" and prior_partial is not None:
        progress_fields = ("producer_id", "milestone", "candidate_revision", "handoff_ref",
                           "next_objective", "required_pending", "evidence_refs", "summary")
        if all(returned[field] == prior_partial.get(field) for field in progress_fields):
            return result("investigate", "repeated partial return supplies no new progress or actionable step")
    if returned["schema"] == V2:
        action, reason = v2_action(returned, assignment, current_binding, accepted_milestones,
                                  current_target_milestones, eligible_milestones)
        return result(action, reason, key if action in {
            "resume-integrator", "fresh-integrator", "pending", "stop", "report-closeout", "relay-review"
        } else None)
    action = {
        "milestone-complete": "fresh-integrator",
        "continue-milestone": "resume-integrator",
        "human-pending": "pending",
        "blocked": "pending",
        "pack-complete": "report-closeout",
        "review-request": "relay-review" if review_relay else "clarify",
    }[returned["disposition"]]
    return result(action, "consume references; engineering judgment remains with the designated integrator", key)


def bind_assignment(root, plan_path, milestone, *, run_id, dispatch_id, producer_id,
                    mandate_revision, projection=None):
    """Compute scope identity from current consumer requirements, without writing."""
    import subprocess
    import milestone_plan as plans
    binding = plans.resolve_binding(root, plan_path, milestone, projection=projection)
    plan = plans.load_plan(plans.safe_path(root, plan_path))
    if binding['references'] != 'resolved' or binding['diagnostics_truncated']:
        raise ValueError('assignment has unresolved requirements: ' + '; '.join(binding['diagnostics']))
    identity = dict(run_id=run_id, dispatch_id=dispatch_id, producer_id=producer_id,
                    mandate_revision=mandate_revision, milestone=milestone)
    if any(not isinstance(value, str) or not value.strip() for value in identity.values()):
        raise ValueError('assignment requires exact native and mandate identities')
    branch = subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip()
    return dict(schema='implement-rfc.milestone-assignment.v1', **identity,
                consumer_root=str(root), branch=branch, binding=binding,
                target_milestones=([milestone] if binding.get('projection') else
                                   [item['id'] for item in plan['milestones']]))


def select_scope(plan, accepted, requested=None):
    import milestone_plan as plans
    default = plans.select_milestone(plan, accepted)
    if requested is None:
        return default
    selected = next((item for item in plan['milestones'] if item['id'] == requested), None)
    if selected is None or requested in accepted or not set(selected['depends_on']) <= set(accepted):
        raise ValueError('requested milestone is absent, already accepted or has pending prerequisites')
    return selected


def independent_milestones(root, config, plan, accepted):
    """Planning may include internal chains; pending outside prerequisites prevent bypass."""
    import milestone_plan as plans
    eligible = []
    for item in plan['milestones']:
        if item['id'] in accepted or not set(item['depends_on']) <= set(accepted):
            continue
        selected = {ref['issue'] for ref in item['work'] if 'issue' in ref}
        rows = plans.planning_observations(root, config, plan, item['work'])['issues']
        if any(row['external_depends_on'] or
               set(row['unresolved_prerequisites']) - selected
               for row in rows if row['id'] in selected):
            continue
        eligible.append(item['id'])
    return eligible


def decision_diagnostics(assignment, returned, action):
    """Compact linkage from supplied records, not reconstructed history or usage."""
    binding = assignment['binding']
    matched = (isinstance(returned, dict) and
               all(returned.get(key) == assignment.get(key) for key in IDENTITY))
    request = returned.get('continuation') if matched else None
    return {'plan_id': binding['plan_id'], 'milestone_id': binding['milestone_id'],
            'producer_id': assignment['producer_id'], 'dispatch_id': assignment['dispatch_id'],
            'generation_index': None,
            'requested_reason': request.get('reason') if isinstance(request, dict) else None,
            'requested_detail': request.get('detail') if isinstance(request, dict) else None,
            'decision': action, 'source': 'supplied assignment and return',
            'economics': 'not inferred'}


def human_report(result, outcome=None):
    binding = result.get('binding', {})
    context = result.get('diagnostics', {})
    if not binding and not context:
        return f"{result.get('action', 'Reconcile')}: {result.get('reason', 'unknown')}"
    plan = binding.get('plan_id', context.get('plan_id'))
    milestone = binding.get('milestone_id', context.get('milestone_id'))
    producer = result.get('producer_id', context.get('producer_id'))
    dispatch = result.get('dispatch_id', context.get('dispatch_id'))
    lines = [f"Plan: {plan}", f"Current: {milestone}" + (f" — {outcome}" if outcome else ''),
             f"Integrator: {producer}; dispatch {dispatch}; generation index unknown"]
    if binding:
        lines.append(f"Assigned: {len(binding['obligations'])} obligations; {len(binding['exit_criteria'])} exits")
    else:
        lines.append(f"Decision: {result['action']} — {result['reason']}")
        lines.append(f"Recorded continuation reason: {context.get('requested_reason') or 'unknown'}")
    return '\n'.join(lines)


def main(argv=None):
    """Public observational composition over plan lookup and native observations."""
    import argparse
    import json
    import subprocess
    import milestone_plan as plans
    import project_config
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('assign', 'check'))
    parser.add_argument('--repo-root', required=True)
    parser.add_argument('--plan')
    parser.add_argument('--target', action='append', default=[])
    parser.add_argument('--milestone')
    parser.add_argument('--projection', help='consumer-relative JSON list of explicitly authorized work references')
    parser.add_argument('--accepted-milestone', action='append', default=[])
    for field in ('run-id', 'dispatch-id', 'producer-id', 'mandate-revision', 'assignment', 'return-file'):
        parser.add_argument('--' + field)
    parser.add_argument('--execution', choices=('active', 'unknown', 'quiescent'), default='unknown')
    parser.add_argument('--consumed', help='consumer-relative JSON list of consumed identity tuples')
    parser.add_argument('--prior-partial', help='consumer-relative previous partial return')
    parser.add_argument('--cancelled', action='store_true')
    parser.add_argument('--review-relay', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    outcome = None
    try:
        ctx = project_config.resolve_context(repo_root=args.repo_root)
        root = ctx.repo_root
        def read(relative):
            return plans.load_json(plans.safe_path(root, relative))
        if args.operation == 'assign':
            found = plans.discover(root, ctx.config, plan=args.plan, targets=args.target)
            if found['state'] != 'found':
                raise ValueError('assignment needs adopted plan: ' + found['state'])
            path = plans.Path(found['path'])
            plan = plans.load_plan(path)
            selected = select_scope(plan, args.accepted_milestone, args.milestone)
            if selected is None:
                raise ValueError('no eligible milestone; reconcile required accepted evidence')
            outcome = selected['outcome']
            result = bind_assignment(root, path.relative_to(root).as_posix(), selected['id'],
                run_id=args.run_id, dispatch_id=args.dispatch_id, producer_id=args.producer_id,
                mandate_revision=args.mandate_revision,
                projection=read(args.projection) if args.projection else None)
        else:
            assignment, returned = read(args.assignment), read(args.return_file)
            errors = assignment_errors(assignment)
            if errors:
                raise ValueError('; '.join(errors))
            branch = subprocess.check_output(['git', '-C', str(root), 'branch', '--show-current'], text=True).strip()
            if assignment.get('consumer_root') != str(root) or assignment.get('branch') != branch:
                raise ValueError('assignment consumer or branch differs')
            binding = assignment.get('binding', {})
            current = plans.resolve_binding(root, binding.get('plan_path'), binding.get('milestone_id'),
                                            projection=binding.get('projection'))
            current_plan = plans.load_plan(plans.safe_path(root, binding['plan_path']))
            outcome = next(item['outcome'] for item in current_plan['milestones']
                           if item['id'] == binding['milestone_id'])
            # Validate prerequisite observations against the parent plan, while
            # projected completion accounts only for its own target milestone.
            plans.select_milestone(current_plan, args.accepted_milestone)
            accepted_target = [mid for mid in args.accepted_milestone if mid in assignment['target_milestones']]
            if isinstance(returned, dict) and returned.get('disposition') == 'pack-complete' and current_plan.get('unplanned_work'):
                raise ValueError('partial plan still has required unplanned work; complete its formation before closeout')
            result = continuation(returned, assignment, execution=args.execution, current_binding=current,
                consumed=read(args.consumed) if args.consumed else (), cancelled=args.cancelled,
                accepted_milestones=accepted_target,
                current_target_milestones=([binding['milestone_id']] if binding.get('projection') else
                                          [item['id'] for item in current_plan['milestones']]),
                eligible_milestones=independent_milestones(root, ctx.config, current_plan,
                                                         args.accepted_milestone),
                review_relay=args.review_relay,
                prior_partial=read(args.prior_partial) if args.prior_partial else None)
            if result['action'] in ('fresh-integrator', 'resume-integrator'):
                request = returned['continuation']
                if binding.get('projection') and request['next_milestone'] != binding['milestone_id']:
                    raise ValueError('projected scope cannot authorize another milestone')
                accepted = list(args.accepted_milestone)
                if returned['disposition'] == 'milestone-complete':
                    accepted.append(binding['milestone_id'])
                plan = plans.load_plan(plans.safe_path(root, binding['plan_path']))
                # A result cannot bypass authored hard prerequisites when choosing
                # its next outcome. Evidence for prior accepted IDs remains caller-owned.
                select_scope(plan, accepted, request['next_milestone'])
            result['diagnostics'] = decision_diagnostics(assignment, returned, result['action'])
        print(json.dumps(result, ensure_ascii=False) if args.json else
              human_report(result, outcome))
        return 0 if result.get('action') not in ('clarify', 'reconcile') else 2
    except (ValueError, OSError, TypeError, KeyError) as error:
        result = {'action': 'reconcile', 'reason': str(error)[:8192], 'consume_key': None,
                  'engineering_acceptance': 'not-evaluated'}
        print(json.dumps(result) if args.json else 'Reconcile: ' + result['reason'])
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
