"""Capability-checked stdio app-server companion using existing ChatGPT auth."""
from __future__ import annotations
from collections import deque
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import tempfile
import threading
import time

MAX_FRAME=1024*1024


class DecisionRequired(RuntimeError):
    pass


class Rpc:
    def __init__(self,executable='codex',timeout=30):
        resolved=shutil.which(executable)
        if not resolved:raise ValueError('Codex CLI unavailable')
        self.timeout=timeout;self.next_id=0;self.pending=deque();self.closed=threading.Event()
        self.incoming=queue.Queue(maxsize=128)
        self.process=subprocess.Popen([resolved,'app-server','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        self.reader=threading.Thread(target=self.read,daemon=True);self.reader.start()
        self.request('initialize',{'clientInfo':{'name':'implement_rfc','version':'1.0'}})
        self.send({'method':'initialized','params':{}})

    def read(self):
        try:
            while not self.closed.is_set():
                raw=self.process.stdout.readline(MAX_FRAME+1)
                if not raw:raise EOFError('App-server stream ended')
                if len(raw)>MAX_FRAME or not raw.endswith(b'\n'):raise ValueError('Oversized or torn app-server frame')
                item=json.loads(raw)
                if not isinstance(item,dict):raise ValueError('Invalid app-server frame')
                self.incoming.put(item,timeout=self.timeout)
        except Exception as error:
            try:self.incoming.put(error,timeout=1)
            except queue.Full:pass

    def send(self,value):
        raw=(json.dumps(value)+'\n').encode()
        if len(raw)>MAX_FRAME:raise ValueError('Request exceeds frame bound')
        self.process.stdin.write(raw);self.process.stdin.flush()

    def receive(self,timeout=None):
        try:item=self.incoming.get(timeout=self.timeout if timeout is None else timeout)
        except queue.Empty:raise TimeoutError('App-server deadline reached') from None
        if isinstance(item,Exception):raise item
        if 'method' in item and 'id' in item:
            # Do not answer permission or authentication requests on the user's behalf.
            raise DecisionRequired('Native host decision required: '+str(item['method']))
        return item

    def request(self,method,params):
        self.next_id+=1;rid=self.next_id
        self.send({'id':rid,'method':method,'params':params})
        deadline=time.monotonic()+self.timeout
        while True:
            value=self.receive(max(.001,deadline-time.monotonic()))
            if value.get('id')==rid:
                if 'error' in value:raise RuntimeError('Native RPC refused '+method+': '+str(value['error'].get('code')))
                return value.get('result',{})
            if len(self.pending)>=128:raise ValueError('Pending native notification budget exceeded')
            self.pending.append(value)

    def notifications(self,seconds):
        deadline=time.monotonic()+seconds
        for _ in range(10000):
            remaining=deadline-time.monotonic()
            if remaining<=0:raise TimeoutError('Native attempt deadline reached')
            yield self.pending.popleft() if self.pending else self.receive(remaining)
        raise ValueError('Native event budget exceeded')

    def close(self):
        self.closed.set()
        if self.process.poll() is None:
            self.process.terminate()
            try:self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:self.process.kill();self.process.wait(timeout=3)
        for stream in (self.process.stdin,self.process.stdout):
            stream.close()
        self.reader.join(timeout=1)


def discover(executable='codex'):
    resolved=shutil.which(executable)
    if not resolved:return {'launch':False,'reason':'cli_missing'}
    with tempfile.TemporaryDirectory(prefix='rfc-codex-capabilities-') as tmp:
        result=subprocess.run([resolved,'app-server','generate-json-schema','--out',tmp],capture_output=True,timeout=30)
        if result.returncode:return {'launch':False,'reason':'schema_discovery_unsupported'}
        required={'ThreadStartParams':{'cwd','model','approvalPolicy','sandbox'},
                  'TurnStartParams':{'threadId','input','effort'},'TurnInterruptParams':{'threadId','turnId'}}
        for name,fields in required.items():
            files=list(Path(tmp).rglob(name+'.json'))
            if len(files)!=1 or not fields <= set(json.loads(files[0].read_text()).get('properties',{})):
                return {'launch':False,'reason':'required_protocol_fields_missing'}
    return {'launch':True,'event_driven':True,'read_only_report_resume':False,
            'native_embedded_subagent_resume':False,'turn_limit':'unsupported','billing':'existing_chatgpt_only',
            'permission_requests':'stop_for_native_host_decision'}


class CodexDriver:
    def __init__(self,executable='codex',rpc=None,capabilities=None):
        self.executable=executable;self.rpc=rpc;self.owned={}
        self._capabilities=capabilities if capabilities is not None else discover(executable)

    def capabilities(self):return dict(self._capabilities)

    def validate(self,packet):
        if not self._capabilities.get('launch'):raise ValueError('Required Codex protocol unsupported')
        if not isinstance(packet,dict) or set(packet)!={'cwd','prompt','model','effort','approval_policy','sandbox','timeout_seconds'}:
            raise ValueError('Explicit native packet fields required')
        if packet['sandbox'] not in ('read-only','workspace-write') or packet['approval_policy'] not in ('never','on-request','untrusted'):
            raise ValueError('Unsupported native permission policy')
        if not Path(packet['cwd']).is_absolute() or not Path(packet['cwd']).is_dir():raise ValueError('Physical cwd required')
        if not isinstance(packet['prompt'],str) or len(packet['prompt'].encode())>128*1024:raise ValueError('Bounded task prompt required')
        if packet['effort'] not in ('low','medium','high','xhigh','max','ultra'):raise ValueError('Unsupported effort')
        if not isinstance(packet['model'],str) or not packet['model']:raise ValueError('Explicit model required')
        if type(packet['timeout_seconds']) is not int or not 1<=packet['timeout_seconds']<=600:raise ValueError('Bounded native deadline required')

    def launch(self,packet,attempt_id):
        self.validate(packet)
        if self.rpc is None:self.rpc=Rpc(self.executable)
        account=self.rpc.request('account/read',{'refreshToken':False})
        if account.get('account',{}).get('type')!='chatgpt':
            raise ValueError('Existing ChatGPT authentication required; no API billing fallback')
        thread=self.rpc.request('thread/start',{'cwd':packet['cwd'],'model':packet['model'],
                    'approvalPolicy':packet['approval_policy'],'sandbox':packet['sandbox']})
        tid=thread['thread']['id']
        # Own the thread before requesting a model turn, including a failed turn-start receipt.
        self.owned[tid]={'packet':dict(packet),'attempt_id':attempt_id,'turn':None}
        turn=self.rpc.request('turn/start',{'threadId':tid,'input':[{'type':'text','text':packet['prompt']}],
                    'model':packet['model'],'effort':packet['effort']})
        turn_id=turn['turn']['id'];self.owned[tid]['turn']=turn_id
        return {'driver_session_id':tid,'driver_turn_id':turn_id}

    def require_owned(self,receipt):
        tid=receipt.get('driver_session_id');owned=self.owned.get(tid)
        if not owned or owned['turn']!=receipt.get('driver_turn_id'):
            raise ValueError('Only this driver’s owned thread/turn can be controlled')
        return owned

    def events(self,receipt):
        owned=self.require_owned(receipt);messages=[]
        try:
            for index,raw in enumerate(self.rpc.notifications(owned['packet']['timeout_seconds'])):
                method=raw.get('method');p=raw.get('params',{})
                tid=p.get('threadId');turn_id=p.get('turnId',p.get('turn',{}).get('id'))
                if method not in ('item/completed','turn/completed'):continue
                if tid!=receipt['driver_session_id'] or turn_id!=receipt['driver_turn_id']:
                    raise ValueError('Native event thread/turn mismatch')
                if method=='item/completed':
                    item=p.get('item',{})
                    if item.get('type')=='agentMessage' and isinstance(item.get('text'),str):
                        if sum(len(x) for x in messages)+len(item['text'])>MAX_FRAME:raise ValueError('Report exceeds bound')
                        messages.append(item['text'])
                        yield {**receipt,'kind':'partial','event_id':str(item['id']),'text':item['text']}
                else:
                    turn=p.get('turn',{});state=turn.get('status')
                    kind='completed' if state=='completed' else 'failed'
                    yield {**receipt,'kind':kind,'event_id':'turn-'+receipt['driver_turn_id'],'report':'\n\n'.join(messages)}
                    return
        except (TimeoutError,DecisionRequired):
            # Interrupt only the owned turn. Never acknowledge an approval automatically.
            self.cancel(receipt)
            raise

    def cancel(self,receipt):
        self.require_owned(receipt)
        self.rpc.request('turn/interrupt',{'threadId':receipt['driver_session_id'],'turnId':receipt['driver_turn_id']})
        return True

    def recover_report(self,receipt,**kwargs):
        raise ValueError('Codex report-only resume is not capability-qualified; inspect retained partial reports')

    def inspect_attempt(self,receipt):
        tid=receipt.get('driver_session_id')
        if tid not in self.owned:return {'status':'completion_unknown','reason':'new_driver_cannot_adopt_unverified_session','automatic_relaunch':False}
        return {'status':'owned','thread_id':tid,'turn_id':self.owned[tid]['turn'],'automatic_relaunch':False}

    def close(self):
        if self.rpc is not None:self.rpc.close()
