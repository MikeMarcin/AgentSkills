"""Bounded Claude print-mode companions; subscription auth and explicit leaf tools."""
from __future__ import annotations
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time
import uuid
from usage_capture import tokens

MAX_FRAME=1024*1024


def discover(executable='claude'):
    resolved=shutil.which(executable)
    if not resolved:return {'launch':False,'reason':'cli_missing'}
    result=subprocess.run([resolved,'--help'],capture_output=True,text=True,timeout=15)
    flags=('--print','--output-format','--session-id','--resume','--tools','--safe-mode','--permission-mode','--effort')
    supported=result.returncode==0 and all(flag in result.stdout for flag in flags)
    return {'launch':supported,'event_driven':True,'read_only_report_resume':supported,
            'embedded_subagent_resume':False,'native_turn_id':'unsupported; logical assignment ID used',
            'turn_limit':'requested_via_max_turns; qualify_installed_runtime','billing':'existing_claude_ai_only'}


def normalize(value,receipt,index):
    if not isinstance(value,dict):raise ValueError('Invalid native stream object')
    if value.get('session_id') and value['session_id']!=receipt['driver_session_id']:
        raise ValueError('Native session mismatch')
    if value.get('type')=='assistant':
        content=value.get('message',{}).get('content',[])
        text='\n'.join(x['text'] for x in content if isinstance(x,dict) and x.get('type')=='text' and isinstance(x.get('text'),str))
        if text:return {**receipt,'kind':'partial','event_id':str(value.get('uuid',index)),'text':text}
    if value.get('type')=='result':
        if value.get('session_id')!=receipt['driver_session_id']:raise ValueError('Final result lacks owned session identity')
        subtype=value.get('subtype')
        kind='completed' if subtype=='success' and value.get('is_error') is not True else 'max_turns' if subtype=='error_max_turns' else 'failed'
        return {**receipt,'kind':kind,'event_id':str(value.get('uuid','result-'+str(index))),
                'report':value.get('result') if isinstance(value.get('result'),str) else None,
                'usage_aggregate_do_not_add':tokens(value.get('usage'))}
    return None


class ClaudeDriver:
    def __init__(self,executable='claude',capabilities=None):
        self.executable=shutil.which(executable) or executable
        self._capabilities=capabilities if capabilities is not None else discover(executable)
        self.owned={}
    def capabilities(self):return dict(self._capabilities)
    def validate(self,packet):
        if not self._capabilities.get('launch'):raise ValueError('Required Claude companion flags unsupported')
        if not isinstance(packet,dict) or set(packet)!={'cwd','prompt','model','effort','tools','max_turns','timeout_seconds'}:
            raise ValueError('Explicit companion packet required')
        if not Path(packet['cwd']).is_absolute() or not Path(packet['cwd']).is_dir():raise ValueError('Native cwd missing')
        if not isinstance(packet['tools'],list) or not set(packet['tools']) <= {'Read','Grep','Glob'}:
            raise ValueError('This companion is a read-only leaf; mutation and delegation tools unsupported')
        for name in ('prompt','model','effort'):
            if not isinstance(packet[name],str) or not packet[name]:raise ValueError('Explicit native route and prompt required')
        if len(packet['prompt'].encode())>128*1024:raise ValueError('Prompt exceeds bound')
        if type(packet['max_turns']) is not int or not 1<=packet['max_turns']<=10:raise ValueError('Turn budget out of range')
        if type(packet['timeout_seconds']) is not int or not 1<=packet['timeout_seconds']<=600:raise ValueError('Deadline out of range')
    def auth(self):
        if any(os.environ.get(k) for k in ('ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN','CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY')):
            raise ValueError('External billing/auth environment is not the subscription companion route')
        result=subprocess.run([self.executable,'auth','status','--json'],capture_output=True,text=True,timeout=15)
        data=json.loads(result.stdout)
        if result.returncode or not data.get('loggedIn') or data.get('authMethod')!='claude.ai' or data.get('apiProvider')!='firstParty':
            raise ValueError('Existing claude.ai subscription authentication required')
    def spawn(self,packet,sid,resume=False):
        command=[self.executable,'--print','--output-format','stream-json','--verbose','--safe-mode',
                 '--tools',','.join(packet['tools']),'--disallowedTools','mcp__*','--permission-mode','dontAsk',
                 '--max-turns',str(packet['max_turns']),'--model',packet['model'],'--effort',packet['effort'],
                 '--resume' if resume else '--session-id',sid,packet['prompt']]
        process=subprocess.Popen(command,cwd=packet['cwd'],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
                                 start_new_session=os.name=='posix')
        return process
    def launch(self,packet,attempt_id):
        self.validate(packet);self.auth()
        sid=str(uuid.uuid4())
        if checkpoint := getattr(self,'identity_checkpoint',None):
            checkpoint(driver_session_id=sid,driver_turn_id='assignment:'+attempt_id,phase='session_allocated')
        process=self.spawn(packet,sid)
        self.owned[sid]={'process':process,'packet':dict(packet),'attempt':attempt_id,'cancelled':False,'recovered':False}
        return {'driver_session_id':sid,'driver_turn_id':'assignment:'+attempt_id}
    def require_owned(self,receipt):
        owned=self.owned.get(receipt.get('driver_session_id'))
        if not owned or receipt.get('driver_turn_id')!='assignment:'+owned['attempt']:raise ValueError('Unknown companion assignment')
        return owned
    def stream(self,process,seconds):
        messages=queue.Queue(maxsize=128);closed=threading.Event()
        def read():
            try:
                while not closed.is_set():
                    raw=process.stdout.readline(MAX_FRAME+1)
                    if not raw:messages.put(None,timeout=1);return
                    if len(raw)>MAX_FRAME or not raw.endswith(b'\n'):raise ValueError('Oversized/torn native stream')
                    messages.put(json.loads(raw),timeout=1)
            except Exception as error:
                try:messages.put(error,timeout=1)
                except queue.Full:pass
        reader=threading.Thread(target=read,daemon=True);reader.start()
        deadline=time.monotonic()+seconds
        try:
            for _ in range(10000):
                try:value=messages.get(timeout=min(.25,max(.001,deadline-time.monotonic())))
                except queue.Empty:
                    if time.monotonic()>=deadline:raise TimeoutError('Companion deadline reached') from None
                    yield {'type':'__idle__'}
                    continue
                if value is None:return
                if isinstance(value,Exception):raise value
                yield value
            raise ValueError('Companion event budget exceeded')
        finally:
            closed.set()
    def events(self,receipt):
        owned=self.require_owned(receipt);final=False
        try:
            for index,value in enumerate(self.stream(owned['process'],owned['packet']['timeout_seconds'])):
                if value.get('type')=='__idle__':
                    yield {'kind':'idle'}
                    continue
                event=normalize(value,receipt,index)
                if event:
                    yield event
                    if event['kind']!='partial':final=True;break
            if not final:raise ValueError('Native process ended without a structured result')
        except Exception:
            self.cancel(receipt);raise
    def cancel(self,receipt):
        owned=self.require_owned(receipt);owned['cancelled']=True
        process=owned['process']
        if process.poll() is None:
            process.terminate()
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
        return True
    def recover_report(self,receipt,budget_seconds):
        owned=self.require_owned(receipt)
        if owned['cancelled'] or owned['recovered']:raise ValueError('Cancelled/already recovered companion')
        if owned['process'].poll() is None:raise ValueError('Companion must finish before report-only resume')
        owned['recovered']=True
        packet={**owned['packet'],'tools':[],'max_turns':1,'timeout_seconds':budget_seconds,
                'prompt':'Return only a compact report of findings already established in this session. No new discovery, tools, edits or delegation.'}
        self.auth();process=self.spawn(packet,receipt['driver_session_id'],resume=True);owned['process']=process
        report=None
        try:
            if owned['cancelled']:
                raise ValueError('Recovery cancelled before stream collection')
            for index,value in enumerate(self.stream(process,budget_seconds)):
                event=normalize(value,receipt,index)
                if event and event['kind']=='completed':report=event.get('report');break
            if not report:raise ValueError('Recovery produced no usable final report')
            return {'driver_session_id':receipt['driver_session_id'],'report':report}
        finally:
            if process.poll() is None:process.terminate();process.wait(timeout=3)
    def inspect_attempt(self,receipt):
        if receipt.get('driver_session_id') not in self.owned:return {'status':'completion_unknown','automatic_relaunch':False}
        owned=self.require_owned(receipt)
        return {'status':'running' if owned['process'].poll() is None else 'terminated','automatic_relaunch':False}
    def close(self):
        for sid,owned in self.owned.items():
            if owned['process'].poll() is None:self.cancel({'driver_session_id':sid,'driver_turn_id':'assignment:'+owned['attempt']})
            owned['process'].stdout.close()
