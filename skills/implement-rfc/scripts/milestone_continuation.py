"""Plan-bound logical completion checks; engineering acceptance stays with its owner."""
import re

V2 = 'implement-rfc.milestone-return.v2'
BINDING_FIELDS = ('plan_id', 'plan_path', 'milestone_id', 'definition_fingerprint',
                  'obligation_fingerprint', 'prerequisite_fingerprint')

def assignment_errors(value):
    required = {'schema','run_id','dispatch_id','producer_id','mandate_revision','milestone',
                'consumer_root','branch','binding','target_milestones'}
    if not isinstance(value, dict) or set(value) != required:
        return ['invalid assignment fields']
    if value['schema'] != 'implement-rfc.milestone-assignment.v1':
        return ['unsupported assignment schema']
    errors = binding_errors(value['binding'])
    if any(not isinstance(value[key], str) or not value[key].strip() for key in
           required - {'binding','target_milestones'}):
        errors.append('invalid assignment identity')
    targets = value['target_milestones']
    if (not isinstance(targets,list) or not targets or any(not isinstance(x,str) or not x for x in targets)
            or len(set(targets)) != len(targets) or value['milestone'] not in targets):
        errors.append('invalid target milestone set')
    if not errors and value['milestone'] != value['binding']['milestone_id']:
        errors.append('assignment milestone differs from binding')
    return errors

def binding_errors(binding):
    if not isinstance(binding, dict):
        return ['missing plan binding']
    errors = []
    required = set(BINDING_FIELDS) | {'obligations', 'exit_criteria', 'structural', 'references',
        'semantic_coverage', 'diagnostics', 'diagnostics_truncated'}
    if not required <= binding.keys() or binding.keys() - required - {'work'}:
        errors.append('invalid binding fields')
    if (binding.get('references') != 'resolved' or binding.get('structural') != 'valid'
        or binding.get('diagnostics_truncated') is not False or binding.get('diagnostics') != []
        or binding.get('semantic_coverage') != 'unknown'):
        errors.append('unresolved or truncated obligation projection')
    for key in BINDING_FIELDS:
        if not isinstance(binding.get(key), str) or not binding[key].strip():
            errors.append('invalid binding ' + key)
        elif key.endswith('fingerprint') and not re.fullmatch(r'sha256:[0-9a-f]{64}', binding[key]):
            errors.append('invalid fingerprint ' + key)
    path = binding.get('plan_path')
    if isinstance(path, str) and (path.startswith('/') or '\\' in path or ':' in path
                                 or any(p in ('', '.', '..') for p in path.split('/'))):
        errors.append('binding plan path must remain consumer-relative')
    for field in ('obligations', 'exit_criteria'):
        values = binding.get(field)
        if not isinstance(values, list) or not values:
            errors.append('missing binding ' + field)
        elif any(not isinstance(item, dict) or not isinstance(item.get('id'), str)
                 or not item['id'].strip() for item in values):
            errors.append('invalid binding ' + field)
        elif len({item['id'] for item in values}) != len(values):
            errors.append('duplicate binding ' + field)
        else:
            for item in values:
                keys = {'id','text'} if field == 'exit_criteria' else {'id','source','selector','source_fingerprint'}
                if set(item) != keys:
                    errors.append('invalid binding record fields')
                elif field == 'exit_criteria':
                    if not isinstance(item['text'], str) or not item['text'].strip():
                        errors.append('invalid exit criterion text')
                elif (not isinstance(item['source'], str) or not item['source'].strip()
                    or not isinstance(item['source_fingerprint'], str)
                    or not re.fullmatch(r'sha256:[0-9a-f]{64}', item['source_fingerprint'])
                    or (item['selector'] is not None and
                        (not isinstance(item['selector'], str) or not item['selector'].strip()))):
                    errors.append('invalid source obligation')
    return errors

def v2_errors(value):
    errors = binding_errors(value.get('binding'))
    if not errors and value['milestone'] != value['binding']['milestone_id']:
        errors.append('return milestone differs from binding')
    request = value.get('continuation')
    if (not isinstance(request, dict)
        or set(request) != {'intent', 'next_milestone', 'reason', 'detail'}
        or request.get('intent') not in ('continue', 'fresh', 'wait', 'stop')
        or request.get('reason') not in ('integrated-boundary', 'related-continuation',
            'context-pressure', 'producer-unavailable', 'ownership-recovery',
            'explicit-user-request', 'current-milestone', 'pending-obligation', 'target-complete')
        or not isinstance(request.get('detail'), str) or not request['detail'].strip()
        or (request.get('next_milestone') is not None and
            (not isinstance(request['next_milestone'], str) or not request['next_milestone'].strip()))):
        errors.append('invalid explicit continuation request')
    records = value.get('acceptance_records')
    if not isinstance(records, list):
        return errors + ['missing acceptance_records']
    ids = []
    for record in records:
        if (not isinstance(record, dict) or set(record) != {'id', 'outcome', 'evidence_refs'}
            or not isinstance(record.get('id'), str) or not record['id'].strip()
            or record.get('outcome') not in ('pass', 'fail', 'pending')
            or not isinstance(record.get('evidence_refs'), list)
            or not record['evidence_refs']
            or any(not isinstance(ref, str) or not ref.strip() for ref in record['evidence_refs'])):
            errors.append('invalid acceptance record')
        else:
            ids.append(record['id'])
            if not set(record['evidence_refs']) <= set(value['evidence_refs']):
                errors.append('acceptance evidence absent from return evidence_refs')
    if len(set(ids)) != len(ids):
        errors.append('duplicate acceptance record')
    if not errors and value['disposition'] in ('milestone-complete', 'pack-complete'):
        expected = {item['id'] for field in ('obligations', 'exit_criteria')
                    for item in value['binding'][field]}
        if set(ids) != expected or any(record['outcome'] != 'pass' for record in records):
            errors.append('completion lacks passing assigned obligations or exit criteria')
        if value['required_pending']:
            errors.append('completion has required pending evidence')
    return errors

def v2_action(returned, assignment, current_binding, accepted_milestones=(), current_target_milestones=None):
    """Return action/reason, after common identity and execution guards."""
    binding = assignment.get('binding')
    if binding_errors(binding):
        return 'reconcile', 'assignment needs resolved plan binding'
    if returned['binding'] != binding:
        return 'ignore-stale', 'result differs from dispatch-bound definition or obligations'
    if current_binding is None or binding_errors(current_binding):
        return 'reconcile', 'current plan and requirement observation is required'
    if any(binding[key] != current_binding[key] for key in
           (*BINDING_FIELDS, 'obligations', 'exit_criteria')):
        return 'reconcile', 'affected plan or requirements changed; renew assignment'
    request = returned['continuation']
    intent, reason, next_id = request['intent'], request['reason'], request['next_milestone']
    complete = returned['disposition'] in ('milestone-complete', 'pack-complete')
    if returned['disposition'] == 'pack-complete':
        if intent != 'stop' or next_id is not None:
            return 'clarify', 'target completion must stop with no next milestone'
        if current_target_milestones is None or assignment['target_milestones'] != current_target_milestones:
            return 'reconcile', 'target milestone set requires current source reconciliation'
        if set(assignment['target_milestones']) - set(accepted_milestones) - {binding['milestone_id']}:
            return 'clarify', 'other assigned target milestones still require accepted evidence'
        return 'report-closeout', request['detail']
    if returned['disposition'] == 'review-request':
        return 'relay-review', 'qualified review returns to the same integrator'
    if intent == 'wait':
        return 'pending', request['detail']
    if intent == 'stop':
        return 'stop', request['detail']
    if not next_id:
        return 'clarify', 'renewed scope must name the intended milestone'
    if not complete and next_id != binding['milestone_id']:
        return 'reconcile', 'unfinished scope cannot silently transfer to another milestone'
    if intent == 'fresh':
        allowed = {'context-pressure', 'producer-unavailable', 'ownership-recovery', 'explicit-user-request'}
        if complete:
            allowed.add('integrated-boundary')
        if reason not in allowed:
            return 'clarify', 'fresh context needs a concrete boundary or recovery reason'
        return 'fresh-integrator', request['detail']
    if complete and reason != 'related-continuation':
        return 'clarify', 'same-context next outcome needs related-continuation reason'
    return 'resume-integrator', request['detail']
