"""Three bounded selected-instance boot snapshots, always resume; no UI action/breakpoints."""
import datetime
import hashlib
import json
import socket
import struct
import sys
import time
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
out = k / 'pending002'
run = ws / 'work/runs/nt5-boundary196-pending002'
dest = out / 'live-observation.json'
assert not dest.exists()
sys.path.insert(0, str(k.parent / 'native-windows-prebuild'))
from monitor_capture import command, acquire_monitor_lock
sys.path.insert(0, str(ws / 'work/python-packages'))
from PIL import Image
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
source = (k.parent / 'native-windows-nt5-kernel/trace-entry.py').read_text(encoding='utf-8')
ns = {}
exec(source[source.index('class Remote:'):source.index('p=argparse.ArgumentParser()')], dict(socket=socket), ns)
Remote = ns['Remote']
result = dict(physical_access=False, ordinary_qualified=False, debugger_observation=True,
              ui_actions=0, breakpoints=0, captures=[], source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
deadline = time.monotonic() + 1150
while not (out / 'launch.json').exists():
    assert time.monotonic() < deadline and not (run / 'cleanup.json').exists()
    time.sleep(.5)
launch = read(out / 'launch.json')['cycles'][0]['launch_requested_utc']
start = datetime.datetime.fromisoformat(launch).timestamp()
for elapsed in [90, 300, 960]:
    while time.time() < start + elapsed:
        if (run / 'cleanup.json').exists() or time.monotonic() >= deadline:
            break
        time.sleep(.5)
    if (run / 'cleanup.json').exists() or time.monotonic() >= deadline:
        break
    instance = read(run / 'instance.json')
    assert instance['taskId'] == 'windows-native-boundary196' and instance['mode'] == 'exclusive'
    art = out / 'artifacts' / ('live-%d' % elapsed)
    art.mkdir(exist_ok=False)
    row = dict(target_elapsed_seconds=elapsed, utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               instance_pid=instance['processId'], images=[], resumed=False)
    lock = acquire_monitor_lock(4594)
    g = None
    running = False
    pause_start = time.monotonic()
    try:
        running = 'VM status: running' in command(4594, 'info status')
        command(4594, 'stop')
        row['registers'] = command(4594, 'info registers')
        g = Remote(4595)
        g.ask('qSupported')
        g.ask('?')
        values = struct.unpack('<9I', bytes.fromhex(g.ask('g'))[:36])
        row['rsp_registers'] = dict(zip(['EAX', 'ECX', 'EDX', 'EBX', 'ESP', 'EBP', 'ESI', 'EDI', 'EIP'], [hex(v) for v in values]))
        try:
            row['stack512'] = g.read(values[4], 512).hex()
            row['eip64'] = g.read(values[8], 64).hex()
        except Exception as exc:
            row['resident_read_error'] = repr(exc)
        # Retain both explicitly labeled geometries, without claiming mode discovery.
        raw = art / 'ram.bin'
        command(4594, 'pmemsave 0 67108864 ' + json.dumps(raw.as_posix()))
        data = raw.read_bytes()
        assert len(data) == 67108864
        row['ram_sha256'] = hashlib.sha256(data).hexdigest()
        for address, width, height, pitch in [(0x03c00000, 1024, 576, 4096), (0x03d04000, 640, 480, 2560)]:
            frame = data[address:address + pitch * height]
            assert len(frame) == pitch * height
            p = art / ('frame-%x-%dx%d.png' % (address, width, height))
            Image.frombytes('RGB', (width, height), frame, 'raw', 'BGRX', pitch, 1).save(p)
            row['images'].append(dict(path=p.relative_to(ws).as_posix(), address=hex(address),
                                     width=width, height=height, pitch=pitch,
                                     geometry_source='Explicit prior192/trace hypotheses, not actual mode discovery',
                                     png_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    except Exception as exc:
        row['error'] = repr(exc)
    finally:
        try:
            if g:
                g.s.close()
            if running:
                command(4594, 'cont')
                row['resumed'] = 'VM status: running' in command(4594, 'info status')
                if not row['resumed']:
                    row['resume_error'] = 'Monitor did not confirm running'
        except Exception as exc:
            row['resume_error'] = repr(exc)
        finally:
            row['pause_transaction_seconds'] = time.monotonic() - pause_start
            lock.close()
            result['captures'].append(row)
            dest.write_text(json.dumps(result, indent=2) + '\n')
        if running and not row['resumed']:
            raise RuntimeError('Owned snapshot could not confirm resume; inspect instance')
    print('Owned196 boot snapshot recorded/resumed at', elapsed, flush=True)
result['closed'] = True
result['closed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
dest.write_text(json.dumps(result, indent=2) + '\n')
