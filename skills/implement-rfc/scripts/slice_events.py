"""Single-writer, append-only attempt events and privacy-safe usage projection."""
from __future__ import annotations
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import time

MAX_EVENT = 65536


class EventStore:
    def __init__(self, root):
        self.root = Path(root)
        if self.root.is_symlink():
            raise ValueError('Event root cannot be a symlink')
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root/'lifecycle.jsonl'
        self.lock_path = self.root/'writer.lock'

    @contextmanager
    def writer(self):
        if self.lock_path.is_symlink() or self.path.is_symlink():
            raise ValueError('Refusing linked state')
        with self.lock_path.open('a+b') as stream:
            if os.name == 'nt':
                import msvcrt
                if stream.tell() == 0:
                    stream.write(b'0');stream.flush()
                stream.seek(0)
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            try:
                yield self
            finally:
                if os.name == 'nt':
                    stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
                else:
                    fcntl.flock(stream.fileno(),fcntl.LOCK_UN)

    def read(self):
        records=[]; warning=None
        if not self.path.exists():
            return records,warning
        with self.path.open('rb') as stream:
            while raw := stream.readline(MAX_EVENT+1):
                if len(raw)>MAX_EVENT:
                    raise ValueError('Oversized lifecycle event')
                if not raw.endswith(b'\n'):
                    warning='torn_final_event';break
                value=json.loads(raw)
                if value.get('sequence') != len(records):
                    raise ValueError('Corrupt lifecycle sequence')
                records.append(value)
                if len(records)>10000:
                    raise ValueError('Lifecycle event budget exceeded')
        return records,warning

    def append(self, event, **data):
        records,warning=self.read()
        if warning:
            raise ValueError('Torn tail requires explicit inspection; no further dispatch')
        if len(records)>=10000:
            raise ValueError('Lifecycle event budget exceeded')
        value={'sequence':len(records),'event':event,'timestamp':time.time(),**data}
        raw=(json.dumps(value,sort_keys=True)+'\n').encode()
        if len(raw)>MAX_EVENT:
            raise ValueError('Event exceeds bound')
        with self.path.open('ab') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        return value


def usage_projection(records):
    """No reports, paths, prompts, credentials or acceptance inference."""
    identities=('run_id','task_id','attempt_id','driver_session_id','driver_turn_id')
    allowed={'dispatch_intent','dispatched','execution_failed','completion_unknown','report_ready','collected',
             'cancel_requested','cancelled','recovery_intent','recovery_report_ready','blocked','awaiting_integration'}
    for record in records:
        if record.get('event') not in allowed:
            continue
        out={key:record[key] for key in ('event','sequence','timestamp')}
        for key in identities:
            if record.get(key) is not None:
                out[key]=hashlib.sha256(str(record[key]).encode()).hexdigest()[:24]
        yield out
