"""Derived task outcomes and exact assignment joins; never a second issue board."""
from __future__ import annotations
from collections import Counter
from usage_capture import dt

STATES={'dispatched','execution_completed','report_ready','collected','accepted','rejected','superseded','reopened','human_repair'}


def validate_experiment(value):
    required={'schema','treatment_id','dimension','comparison_basis','fixed','ceiling','acceptance_ref','decision'}
    if not isinstance(value,dict) or set(value)!=required or value['schema']!='implement-rfc.experiment.v1':
        raise ValueError('Explicit versioned experiment fields required')
    if value['dimension'] not in ('orchestration','routing','instructions'):raise ValueError('One changed dimension per treatment')
    if value['comparison_basis'] not in ('frozen_matched_tasks','observational_real_backlog'):raise ValueError('Unknown comparison basis')
    if not isinstance(value['fixed'],dict) or not {'source','review','context','routes','topology'}<=set(value['fixed']):raise ValueError('Fixed conditions required')
    ceiling=value['ceiling']
    if not isinstance(ceiling,dict) or type(ceiling.get('task_count')) is not int or not 1<=ceiling['task_count']<=100 or not ceiling.get('owner_approval_ref'):
        raise ValueError('Explicit bounded task count and approval reference required')
    if not value['acceptance_ref'] or value['decision'] not in ('pending','inconclusive','keep_opt_in','promote','rollback'):raise ValueError('Outcome/acceptance reference required')
    if value['comparison_basis']=='observational_real_backlog' and value['decision']=='promote':raise ValueError('Observational unmatched tasks alone cannot establish promotion')
    return value


class Outcomes:
    def __init__(self,document=None):
        document=document or {'schema':'implement-rfc.outcomes.v1','assignments':[],'events':[]}
        if document.get('schema')!='implement-rfc.outcomes.v1':raise ValueError('Unknown outcome schema')
        self.assignments=document.get('assignments',[]);events=document.get('events',[])
        if not isinstance(self.assignments,list) or not isinstance(events,list) or len(self.assignments)>10000 or len(events)>50000:raise ValueError('Outcome input exceeds bounds')
        self.tasks={};self.counts=Counter();self.token_totals=Counter();self.unknown=Counter()
        seen={}
        for event in sorted(events,key=lambda e:e.get('timestamp','')):
            if event.get('state') not in STATES or not event.get('task_id') or not event.get('evidence_ref') or dt(event.get('timestamp')) is None:
                raise ValueError('Outcome events require state/task/time/evidence reference')
            eid=event.get('event_id')
            if not eid:raise ValueError('Outcome event identity required')
            if eid in seen:
                if seen[eid]!=event:raise ValueError('Conflicting outcome identity')
                continue
            seen[eid]=event
            state=event['state'];self.counts[state]+=1
            task=self.tasks.setdefault(event['task_id'],{'accepted':False,'produced':False,'collected':False,'human_repair_minutes':0,'evidence_refs':[]})
            if state=='report_ready':task['produced']=True
            if state=='collected':task['collected']=True
            if state in ('accepted','rejected','superseded','reopened'):task['accepted']=state=='accepted'
            if state=='human_repair':
                minutes=event.get('minutes')
                if type(minutes) not in (int,float) or minutes<0:raise ValueError('Explicit nonnegative observed repair minutes required')
                task['human_repair_minutes']+=minutes
            task['evidence_refs'].append(event['evidence_ref'])
        for assignment in self.assignments:
            if not isinstance(assignment,dict) or not all(assignment.get(k) for k in ('session','task_id','attempt_id','evidence_ref')):
                raise ValueError('Assignment requires session/task/attempt/evidence')
            if not dt(assignment.get('since')) or not dt(assignment.get('until')) or dt(assignment['since'])>=dt(assignment['until']):
                raise ValueError('Assignment interval required')

    def assign(self,row):
        task=row.get('task_id')
        if task and row.get('attempt_id'):
            return task
        # An aggregate spanning unidentified requests cannot be assigned from its final timestamp.
        if row.get('classification')!='request_reconciled':return None
        moment=dt(row.get('timestamp'))
        candidates=[a for a in self.assignments if a['session']==row.get('session') and moment and dt(a['since'])<=moment<dt(a['until'])]
        if len(candidates)!=1:return None
        return candidates[0]['task_id']

    def observe(self,row):
        task=self.assign(row)
        if task is None:self.counts['unassigned_ledger_rows']+=1;return
        if row['classification'] not in ('request_reconciled','aggregate_only'):
            self.unknown[task]+=1;return
        counts=row.get('tokens') or {}
        if counts.get('input_tokens') is None or counts.get('output_tokens') is None:self.unknown[task]+=1;return
        self.token_totals[task]+=counts['input_tokens']+counts['output_tokens']

    def summary(self):
        accepted=[task for task,value in self.tasks.items() if value['accepted']]
        all_tokens=sum(self.token_totals.values())
        return {'tasks':self.tasks,'events':dict(self.counts),'accepted_task_count':len(accepted),
                'all_assigned_attempt_tokens':all_tokens,'unknown_rows_by_task':dict(self.unknown),
                'observed_tokens_per_accepted_task':all_tokens/len(accepted) if accepted and all(task in self.token_totals for task in accepted) and not self.unknown and not self.counts['unassigned_ledger_rows'] else None,
                'limitation':'Includes joined failures, recovery, review and repair; unassigned/unknown rows prevent an exact all-in ratio. No acceptance inferred from collection.'}
