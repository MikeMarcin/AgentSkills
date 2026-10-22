"""Disposable CLI fixture: model foreground config lifetime, never contact Tailscale."""
import json
import os
from pathlib import Path
import signal
import sys
import time
from contextlib import contextmanager

root = Path(os.environ['FAKE_TAILSCALE_ROOT'])
config_path = root / 'config.json'

@contextmanager
def config():
    mutex = root / 'mutex'
    while True:
        try:
            mutex.mkdir()
            break
        except FileExistsError:
            time.sleep(.01)
    try:
        value = json.loads(config_path.read_text())
        yield value
        temporary = root / f'config-{os.getpid()}.json'
        temporary.write_text(json.dumps(value))
        temporary.replace(config_path)
    finally:
        mutex.rmdir()

args = sys.argv[1:]
with (root / 'commands.jsonl').open('a') as stream:
    stream.write(json.dumps(args) + '\n')
if args == ['status', '--json']:
    print(json.dumps({'BackendState': 'Running', 'Self': {'Online': True, 'DNSName': 'review.example.ts.net.'}}))
elif args == ['serve', 'status', '--json']:
    print(config_path.read_text())
else:
    assert args[0:2] == ['serve', '--bg=false'], args
    assert len(args) == 4 and args[2].startswith('--https=') and args[3].startswith('http://127.0.0.1:'), args
    mode = (root / 'mode').read_text() if (root / 'mode').exists() else ''
    if mode == 'consent':
        print('Serve is not enabled. Visit https://login.tailscale.com/f/serve?node=disposable', flush=True)
    elif mode == 'fail':
        sys.exit('fixture startup failure')
    identity = f'fixture-{os.getpid()}'
    port = args[2].split('=')[1]
    if mode != 'consent':
        with config() as value:
            value.setdefault('Foreground', {})[identity] = {
                'TCP': {port: {'HTTPS': True}},
                'Web': {f'review.example.ts.net:{port}': {'Handlers': {'/': {'Proxy': args[3]}}}}}
            if mode == 'race':
                value['Foreground']['racing-owner'] = {'TCP': {port: {'HTTPS': True}}}
    running = True
    def stop(*_):
        global running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        deadline = time.monotonic() + (.8 if mode == 'runtime-exit' else 300)
        while running and time.monotonic() < deadline:
            time.sleep(.02)
    finally:
        with config() as value:
            value.get('Foreground', {}).pop(identity, None)
            if not value.get('Foreground'):
                value.pop('Foreground', None)
