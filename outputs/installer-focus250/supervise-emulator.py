"""One ordinary launch; dashboard return or bounded owned host closure, no relaunch."""
import datetime,ftplib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control001','preserve001'];out=k/case;run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/phase250-runs/nt5-phase250-'+case)
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
dest=out/'launch.json';assert not dest.exists() and (run/'instance.json').exists() and not (run/'cleanup.json').exists()
r=dict(run=run.name,host='127.0.0.1',port=4596,debugger=True,physical_access=False,cycles=[])
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');temp.replace(dest)
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+6))
    try:f.connect('127.0.0.1',4596,timeout=f.budget());f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);return f
    except Exception:f.close();raise
deadline=time.monotonic()+180
while not (run/'startup-ready.json').exists():
    assert time.monotonic()<deadline and not (run/'cleanup.json').exists(),'Startup barrier failed; no launch'
    time.sleep(.2)
assert json.loads((run/'startup-ready.json').read_text(encoding='utf-8-sig'))['nic_ready']
# Trace owns prelaunch FTP. Observer opens no connection before trace closes.
while not (out/'trace-finished.signal').exists():
    assert time.monotonic()<deadline and not (run/'cleanup.json').exists(),'Pre-loader phase not finished; no launch'
    time.sleep(.2)
trace=json.loads((out/'trace.json').read_text())
assert trace['closed'] and trace.get('guest_resumed') and not trace['remaining_breakpoints'] and trace.get('physical_mode_restored'), 'Unsafe diagnostic phase; no Windows launch'
assert not (run/'cleanup.json').exists()
# Trace owns the SINGLE loader launch and two executing-code stops.
assert trace['loader_launch']['status']=='accepted'
row=dict(trace['loader_launch']);r['cycles'].append(row);save()
r['diagnostic_passed']=trace['passed'];save()
print('Observing trace-owned single238 launch, never relaunch',flush=True)
deadline=time.monotonic()+520;offline=False
while time.monotonic()<deadline:
    if (run/'cleanup.json').exists():
        row.update(offline_observed=offline,dashboard_return=False,owned_closure_observed_utc=utc())
        r['status']='owned_host_bound_closed_pending_cold_audit';save();break
    time.sleep(2)
    try:
        f=connect(deadline);f.close()
        if offline:
            row.update(offline_observed=True,dashboard_return=True,dashboard_return_utc=utc())
            assert not (run/'cleanup.json').exists()
            r['status']='return_pending_cold_audit';save();(run/'capture-complete.signal').touch(exist_ok=False);break
    except ftplib.all_errors:offline=True
else:
    r['status']='observer_deadline';save();raise RuntimeError('Owned runner did not close within its bound; inspect, never relaunch')
print(r['status'],flush=True)
