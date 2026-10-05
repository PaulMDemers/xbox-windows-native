"""Launch one owned local emulator probe and observe dashboard return, never hardware."""
import datetime
import ftplib
import json
import os
from pathlib import Path
import time

k = Path(__file__).resolve().parent
run = k.parents[2] / 'work/runs/nt5-gdi-baseline-003'
report_path = k / 'launch.json'
assert (run / 'instance.json').exists() and not (run / 'cleanup.json').exists()
assert not report_path.exists()
password = os.environ['XWN_EMULATOR_FTP_PASSWORD']
user = os.environ['XWN_EMULATOR_FTP_USER']
report = {'run': run.name, 'host': '127.0.0.1', 'port': 4596,
          'physical_access': False, 'prelaunch_errors': []}

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

deadline = time.monotonic() + 60
while True:
    try:
        f = connect()
        break
    except ftplib.all_errors as exc:
        report['prelaunch_errors'].append(type(exc).__name__)
        if time.monotonic() >= deadline:
            report['status'] = 'dashboard_unavailable_no_launch'; save()
            raise
        time.sleep(2)
try:
    f.cwd('/E/Applications/XWNFBoot')
    report.update(status='requesting', launch_requested_utc=utc(),
                  command='SITE EXEC E:\\Applications\\XWNFBoot\\default.xbe')
    save()
    # Never retry this command, including an ambiguous reply.
    try:
        report.update(reply=f.sendcmd(report['command']), status='accepted')
    except ftplib.all_errors as exc:
        report.update(status='reply_uncertain', error=type(exc).__name__)
    save()
finally:
    f.close()
print(json.dumps({'status': report['status'], 'run': run.name}), flush=True)

offline = False
deadline = time.monotonic() + 180
while time.monotonic() < deadline:
    time.sleep(8)
    try:
        f = connect()
        try:
            f.quit()
        finally:
            f.close()
        if offline:
            report.update(dashboard_return_utc=utc(), offline_observed=True,
                          dashboard_return=True, workload_result='pending cold audit')
            save()
            (run / 'capture-complete.signal').touch(exist_ok=False)
            print('Dashboard returned; cold audit required', flush=True)
            break
    except ftplib.all_errors:
        offline = True
else:
    report.update(dashboard_return=False, offline_observed=offline,
                  observation='No dashboard return before bounded supervisor ended; no crash inference')
    save()
    print('No dashboard return; guest retained for inspection', flush=True)
