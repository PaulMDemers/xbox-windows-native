"""Single debugger-observed Windows launch via owned loopback; no physical access."""
import datetime,ftplib,json,os,sys,time,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'gpu-reset-banner152'))
from ftp_deadline import DeadlineFTP
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1]
assert case in ['candidate001'];out=k/case;run=ws/('work/runs/nt5-vtoken175-'+case)
p=out/'launch.json';assert not p.exists()
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
assert (out/'trace-armed.signal').exists()
r=dict(run=run.name,host='127.0.0.1',port=4596,physical_access=False,debugger=True,cycles=[])
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    temp=p.with_suffix('.tmp');temp.write_text(json.dumps(r,indent=2)+'\n');temp.replace(p)
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+8))
    try:
        f.connect('127.0.0.1',4596,timeout=f.budget())
        f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);return f
    except Exception:f.close();raise
try:
    deadline=time.monotonic()+60
    while True:
        assert not (run/'cleanup.json').exists()
        try:f=connect(deadline);break
        except ftplib.all_errors:
            if time.monotonic()>=deadline:raise
            time.sleep(min(1,max(0,deadline-time.monotonic())))
    subprocess.run(['pwsh','-NoProfile','-File',str(k/'check-leases.ps1'),'-Case',case,'-Phase','before'],check=True)
    row=dict(cycle=1,status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe',
             trace_before_launch_offset=(run/'cpu-trace.log').stat().st_size)
    r['cycles'].append(row);save()
    try:
        try:row.update(reply=f.sendcmd(row['command']),status='accepted')
        except ftplib.all_errors as exc:row.update(status='reply_uncertain',error=type(exc).__name__)
        row['trace_after_launch_reply_offset']=(run/'cpu-trace.log').stat().st_size;save()
    finally:f.close()
    print('Single Windows launch requested; bounded read-only debugger, no UI/data/register changes',flush=True)
    deadline=time.monotonic()+420;offline=False
    while time.monotonic()<deadline:
        assert not (run/'cleanup.json').exists(),'Owned runner closed'
        time.sleep(min(2,max(0,deadline-time.monotonic())))
        try:
            f=connect(deadline);f.close()
            if offline:
                returned=utc()
                subprocess.run(['pwsh','-NoProfile','-File',str(k/'check-leases.ps1'),'-Case',case,'-Phase','after'],check=True)
                row.update(dashboard_return_utc=returned,offline_observed=True,dashboard_return=True)
                r['status']='return_pending_cold_audit';save();
                trace_deadline=time.monotonic()+20
                while not (out/'trace-closed.signal').exists() and time.monotonic()<trace_deadline:time.sleep(0.25)
                assert (out/'trace-closed.signal').exists(),'Tracer must tear down before runner cleanup'
                (run/'capture-complete.signal').touch(exist_ok=False)
                print('Dashboard returned; correctness pending cold audit',flush=True);break
        except ftplib.all_errors:offline=True
    else:raise RuntimeError('No dashboard return; never relaunch')
except Exception as exc:
    r.update(failed=True,error=repr(exc));save()
    (out/'trace-stop.signal').touch(exist_ok=True)
    trace_deadline=time.monotonic()+30
    while not (out/'trace-closed.signal').exists() and time.monotonic()<trace_deadline:time.sleep(0.25)
    r['tracer_closed_before_cleanup']=(out/'trace-closed.signal').exists();save()
    if not (run/'cleanup.json').exists() and not (run/'capture-complete.signal').exists():
        if r['tracer_closed_before_cleanup']:(run/'capture-complete.signal').touch(exist_ok=False)
    raise
