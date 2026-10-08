"""Launch one owned local emulator probe and observe dashboard return, never hardware."""
import datetime
from atomic_json import write_json
import ftplib
import json
import os
import sys
from pathlib import Path
import time

root = Path(__file__).resolve().parent
case = sys.argv[1]; assert case in ['control001','candidate001']
k = root / case
k.mkdir(exist_ok=True)
run = root.parents[1] / ('work/runs/nt5-vdeskapi-'+case)
report_path = k / 'launch.json'
assert (run / 'instance.json').exists() and not (run / 'cleanup.json').exists()
assert not report_path.exists()
assert (k/'trace-armed.signal').exists()
password = os.environ['XWN_EMULATOR_FTP_PASSWORD']
user = os.environ['XWN_EMULATOR_FTP_USER']
report = {'run': run.name, 'host': '127.0.0.1', 'port': 4596,
          'physical_access': False, 'prelaunch_errors': [], 'cycles': []}

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save():
    write_json(report_path, report)

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
    offline=False;deadline=time.monotonic()+900
    while time.monotonic()<deadline:
        assert not (run/'cleanup.json').exists(), 'Owned emulator has closed'
        time.sleep(8)
        try:
            f=connect();f.close()
            if offline:
                row.update(dashboard_return_utc=utc(),offline_observed=True,dashboard_return=True);save()
                print('Dashboard returned after cycle '+str(cycle)+'; correctness pending cold audit',flush=True)
                break
        except ftplib.all_errors:offline=True
    else:
        row.update(dashboard_return=False,offline_observed=offline);save()
        raise RuntimeError('No dashboard return; never launch next cycle after timeout')
report['status']='one_dashboard_return_pending_cold_audit';save()
deadline=time.monotonic()+660
while not (k/'trace-closed.signal').exists():
    assert not (run/'cleanup.json').exists(), 'Owned runner closed before observer'
    if time.monotonic()>=deadline:
        report['observer_close_timeout']=True;save();raise RuntimeError('Observer did not close; retain owned runner bound')
    time.sleep(1)
trace=json.loads((k/'trace.json').read_text())
report['observer_closed']=True
report['observer_teardown_ok']=trace.get('guest_resumed') is True and not trace.get('armed_breakpoints_remaining') and not trace.get('resume_error')
report['observer_status']=trace['status'];save()
(run/'capture-complete.signal').touch(exist_ok=False)
