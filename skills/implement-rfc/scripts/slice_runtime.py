"""Durable owned native attempts. Drivers deliver facts; integrators decide acceptance."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
from slice_events import EventStore

TOKEN=re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z')
MAX_REPORT=1024*1024


class Runtime:
    def __init__(self, root, driver, run_id):
        if not TOKEN.fullmatch(run_id):raise ValueError('Invalid run ID')
        self.store=EventStore(root)
        self.driver=driver
        self.run_id=run_id

    def records(self, attempt):
        records,warning=self.store.read()
        if warning:raise ValueError('Torn event stream; inspect before mutation')
        return [r for r in records if r.get('attempt_id')==attempt]

    def append(self,event,task,attempt,**data):
        return self.store.append(event,run_id=self.run_id,task_id=task,attempt_id=attempt,**data)

    def dispatch(self,task,packet,*,recovery_budget=0):
        if not TOKEN.fullmatch(task) or type(recovery_budget) is not int or not 0<=recovery_budget<=120:
            raise ValueError('Invalid task or recovery budget')
        attempt=task+'-1'
        with self.store.writer():
            if self.records(attempt):
                raise ValueError('Attempt already admitted; inspect, never relaunch')
            capabilities=self.driver.capabilities()
            if not capabilities.get('launch'):
                return self.append('blocked',task,attempt,reason='unsupported_driver')
            # Drivers must validate the packet and native restrictions before intent/launch.
            self.driver.validate(packet)
            self.append('dispatch_intent',task,attempt,recovery_budget=recovery_budget)
            try:
                receipt=self.driver.launch(packet,attempt_id=attempt)
                if not isinstance(receipt,dict) or not receipt.get('driver_session_id') or not receipt.get('driver_turn_id'):
                    raise ValueError('Driver receipt lacks exact owned identity')
                return self.append('dispatched',task,attempt,driver_session_id=receipt['driver_session_id'],driver_turn_id=receipt['driver_turn_id'])
            except Exception as error:
                self.append('completion_unknown',task,attempt,reason=type(error).__name__)
                raise

    def receipt(self,attempt):
        records=self.records(attempt)
        return next((r for r in reversed(records) if r['event']=='dispatched'),None)

    def save_report(self,task,attempt,text,recovery=False):
        if not isinstance(text,str) or len(text.encode())>MAX_REPORT:
            raise ValueError('Missing or oversized report')
        name=attempt+('.recovery-report.txt' if recovery else '.report.txt')
        path=self.store.root/name
        # Retry collection can reuse precisely identical bytes, never replace a different report.
        raw=text.encode()
        if path.exists() or path.is_symlink():
            if path.is_symlink() or path.read_bytes()!=raw:
                raise ValueError('Report collision')
        else:
            with path.open('xb') as stream:
                stream.write(raw);stream.flush();os.fsync(stream.fileno())
        self.append('recovery_report_ready' if recovery else 'report_ready',task,attempt,
                    report_path=name,sha256=hashlib.sha256(raw).hexdigest())
        self.append('collected',task,attempt,report_path=name)
        return self.records(attempt)[-1]

    def consume(self,attempt,events):
        # This consumes driver events; it never calls a model to check status.
        with self.store.writer():
            receipt=self.receipt(attempt)
            if not receipt:raise ValueError('No owned native receipt; inspect uncertain dispatch')
            task=receipt['task_id']
            records=self.records(attempt)
            seen={r.get('native_event_id') for r in records if r.get('native_event_id')}
            terminal=any(r['event'] in ('cancelled','cancel_requested','awaiting_integration') for r in records)
            for index,event in enumerate(events):
                if index>=10000:raise ValueError('Driver event budget exceeded')
                if event.get('kind')=='idle':continue
                if any(event.get(k)!=receipt[k] for k in ('driver_session_id','driver_turn_id')):
                    raise ValueError('Native event identity mismatch')
                eid=event.get('event_id')
                if not isinstance(eid,str) or len(eid)>256:raise ValueError('Native event identity required')
                if eid in seen:continue
                seen.add(eid)
                if terminal:continue
                kind=event.get('kind')
                if kind=='report':
                    if not any(r['event']=='collected' for r in self.records(attempt)):
                        self.save_report(task,attempt,event.get('text'))
                    if any(r['event']=='execution_completed' for r in self.records(attempt)):
                        self.append('awaiting_integration',task,attempt)
                        terminal=True
                elif kind in ('completed','failed','max_turns','quota'):
                    if kind == 'completed':
                        self.append('execution_completed',task,attempt,native_event_id=eid)
                    if kind == 'completed' and any(r['event']=='collected' for r in self.records(attempt)):
                        self.append('awaiting_integration',task,attempt);terminal=True
                    elif isinstance(event.get('report'),str) and event['report'].strip():
                        self.save_report(task,attempt,event['report'])
                        self.append('awaiting_integration',task,attempt,execution_outcome=kind);terminal=True
                    else:
                        self.append('execution_failed' if kind in ('failed','max_turns') else 'blocked' if kind=='quota' else 'completion_unknown',
                                    task,attempt,reason=kind,native_event_id=eid)
                elif kind=='partial':
                    text=event.get('text')
                    if isinstance(text,str) and len(text.encode())<=MAX_REPORT:
                        # Keep each bounded phase report; arrival order cannot erase earlier evidence.
                        name=attempt+'.partial-'+hashlib.sha256(eid.encode()).hexdigest()[:16]+'.txt'
                        with (self.store.root/name).open('xb') as stream:
                            stream.write(text.encode());stream.flush();os.fsync(stream.fileno())
                        self.append('partial_report_ready',task,attempt,report_path=name,native_event_id=eid)
                else:
                    raise ValueError('Unsupported native lifecycle event')
                self.append('native_event_handled',task,attempt,native_event_id=eid)
            return self.records(attempt)

    def cancel(self,attempt):
        with self.store.writer():
            receipt=self.receipt(attempt)
            if not receipt:raise ValueError('No owned receipt; native cancellation requires inspection')
            records=self.records(attempt)
            if any(r['event'] in ('cancelled','cancel_requested') for r in records):return records
            task=receipt['task_id']
            self.append('cancel_requested',task,attempt)
            try:ack=self.driver.cancel(receipt)
            except Exception:ack=False
            return self.append('cancelled' if ack is True else 'completion_unknown',task,attempt,reason='intentional_cancellation')

    def inspect(self,attempt):
        records=self.records(attempt)
        if not records:raise ValueError('Unknown attempt')
        # Native inspection must be observational, using durable attempt or session/turn IDs.
        return {'records':records,'native':self.driver.inspect_attempt(self.receipt(attempt) or {'attempt_id':attempt}),
                'automatic_relaunch':False}

    def recover_report(self,attempt):
        with self.store.writer():
            records=self.records(attempt);receipt=self.receipt(attempt)
            if not receipt:raise ValueError('Cannot resume an uncertain launch')
            task=receipt['task_id']; events={r['event'] for r in records}
            if events & {'cancel_requested','cancelled','recovery_intent','collected'}:
                raise ValueError('Cancelled, collected or previously recovered attempts cannot resume')
            budget=next((r.get('recovery_budget',0) for r in records if r['event']=='dispatch_intent'),0)
            eligible=any(r.get('reason')=='max_turns' for r in records)
            caps=self.driver.capabilities()
            if not eligible or not budget or not caps.get('read_only_report_resume'):
                return self.append('blocked',task,attempt,reason='report_only_recovery_unsupported_or_not_preapproved')
            self.append('recovery_intent',task,attempt,budget_seconds=budget)
            try:
                result=self.driver.recover_report(receipt,budget_seconds=budget)
                if result.get('driver_session_id')!=receipt['driver_session_id']:
                    raise ValueError('Recovery session changed')
                self.save_report(task,attempt,result.get('report'),recovery=True)
                return self.append('awaiting_integration',task,attempt,recovered_report_only=True)
            except Exception as error:
                return self.append('blocked',task,attempt,reason='recovery_failed_'+type(error).__name__)
