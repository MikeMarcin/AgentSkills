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
             'cancel_requested','cancelled','recovery_intent','recovery_report_ready','blocked','awaiting_integration',
             'native_identity','execution_completed','usage_aggregate_observed'}
    for record in records:
        if record.get('event') not in allowed:
            continue
        out={key:record[key] for key in ('event','sequence','timestamp')}
        for key in identities:
            if record.get(key) is not None:
                out[key]=hashlib.sha256(str(record[key]).encode()).hexdigest()[:24]
        if record.get('event') == 'usage_aggregate_observed':
            from usage_capture import tokens
            out.update(tokens=tokens(record.get('tokens')),additive=False)
        yield out


def capture_runtime_events(projects, output, since, until):
    """Read only selected consumer journals; no reports, orders, prompts or launches."""
    stats = {'files':0, 'events':0, 'warnings':0}
    seen = set()
    with Path(output).open('x', encoding='utf-8') as target:
        for label, root in projects.primary:
            folder = Path(root) / '.mask/generated/implement-rfc/runs'
            if any(p.is_symlink() for p in (folder, *list(folder.parents)[:3])):
                stats['warnings'] += 1
                continue
            if not folder.is_dir():
                continue
            for index, run in enumerate(folder.iterdir()):
                if index >= 1000:
                    stats['warnings'] += 1
                    break
                if run.is_symlink() or not run.is_dir():
                    continue
                for name in ('events.jsonl','lifecycle.jsonl'):
                    path = run / name
                    if path.is_symlink():
                        stats['warnings'] += 1; continue
                    try:
                        if not path.is_file():continue
                        st = path.stat(); identity = (st.st_dev, st.st_ino)
                        if identity in seen:continue
                        seen.add(identity);stats['files'] += 1
                        with path.open('rb') as source:
                            remaining = st.st_size
                            for _ in range(10000):
                                if remaining <= 0:break
                                raw = source.readline(min(MAX_EVENT+1,remaining))
                                remaining -= len(raw)
                                if not raw or len(raw)>MAX_EVENT or not raw.endswith(b'\n'):
                                    stats['warnings'] += 1;break
                                record = json.loads(raw)
                                stamp = record.get('timestamp')
                                if type(stamp) not in (float,int) or not since.timestamp() <= stamp < until.timestamp():continue
                                record.setdefault('sequence',_)
                                record.setdefault('run_id',run.name)
                                for value in usage_projection([record]):
                                    value.update(schema='implement-rfc.runtime-observation.v1', project=label,
                                                 source_id=hashlib.sha256(str(path).encode()).hexdigest()[:24])
                                    target.write(json.dumps(value,sort_keys=True)+'\n')
                                    stats['events'] += 1
                            if remaining>0:stats['warnings'] += 1
                        if path.stat().st_size != st.st_size:stats['warnings'] += 1
                    except (OSError,ValueError,TypeError,AttributeError):
                        stats['warnings'] += 1
    return stats
