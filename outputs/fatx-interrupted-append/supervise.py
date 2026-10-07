"""Launch one owned local emulator probe and observe dashboard return, never hardware."""
import datetime
import ftplib
import json
import os
import sys
from pathlib import Path
import time

root = Path(__file__).resolve().parent
case = sys.argv[1]; assert case in ['001','002','003']
k = root / case
k.mkdir(exist_ok=True)
run = root.parents[1] / ('work/runs/nt5-fatx-interrupted-append-'+case)
report_path = k / 'launch.json'
assert (run / 'instance.json').exists() and not (run / 'cleanup.json').exists()
assert not report_path.exists()
assert (k/'trace-armed.signal').exists(), 'Trace must be armed before the single launch'
password = os.environ['XWN_EMULATOR_FTP_PASSWORD']
user = os.environ['XWN_EMULATOR_FTP_USER']
report = {'run': run.name, 'host': '127.0.0.1', 'port': 4596,
          'physical_access': False, 'prelaunch_errors': [], 'cycles': []}

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save():
    report_path.write_text(json.dumps(report, indent=2) + '\n')

def connect():
    f = ftplib.FTP()
    try:
        f.connect('127.0.0.1', 4596, timeout=3)
        f.login(user, password)
        return f
    except Exception:
        f.close()
        raise


for cycle in [1]:
    deadline=time.monotonic()+60
    while True:
        assert not (run/'cleanup.json').exists(), 'Owned emulator has closed'
        try:f=connect();break
        except ftplib.all_errors as exc:
            report['prelaunch_errors'].append(type(exc).__name__)
            if time.monotonic()>=deadline:save();raise
            time.sleep(2)
    row=dict(cycle=cycle,status='requesting',launch_requested_utc=utc(),command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe')
    report['cycles'].append(row);save()
    try:
        try:row.update(reply=f.sendcmd(row['command']),status='accepted')
        except ftplib.all_errors as exc:row.update(status='reply_uncertain',error=type(exc).__name__)
        save()
    finally:f.close()
    print(json.dumps(row),flush=True)
    # Single launch only. The tracer owns the exact paused checkpoint and exit.
    deadline=time.monotonic()+660
    while time.monotonic()<deadline:
        time.sleep(2)
        state=json.loads((k/'trace.json').read_text())
        if state.get('ended_utc'):
            report.update(status='tracer_finished',trace_status=state['status'],checkpoint_reached=state.get('checkpoint_reached',False),guest_resumed=state.get('guest_resumed'))
            save()
            if not state.get('checkpoint_reached'):
                # Failed diagnostic is closed, never allowed to masquerade as a normal run.
                if not (run/'cleanup.json').exists():(run/'capture-complete.signal').touch(exist_ok=False)
            break
    else:raise RuntimeError('Tracer deadline exceeded; inspect owned state, do not relaunch')
    for _ in range(30):
        if (run/'cleanup.json').exists():
            report.update(cleanup_observed_utc=utc(),status='closed_interrupted_attempt' if report['checkpoint_reached'] else 'closed_failed_attempt');save();break
        time.sleep(1)
    else:raise RuntimeError('Owned emulator cleanup not observed')
