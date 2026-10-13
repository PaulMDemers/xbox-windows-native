"""One ordinary launch; dashboard return or bounded owned host closure, no relaunch."""
import datetime,ftplib,json,os,subprocess,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;run=Path('C:/xwn371/runs/nt5-stretch371-'+case)
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
dest=out/'launch.json';assert not dest.exists() and (run/'instance.json').exists() and not (run/'cleanup.json').exists()
r=dict(run=run.name,host='127.0.0.1',port=5248,debugger=False,physical_access=False,cycles=[])
# Recover only the documented local fixture defaults; never read console config.
import ast
tree=ast.parse((k.parent/'native-windows-prebuild/launch_unleashx.py').read_text())
login=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='login')
for name,arg in zip(['XWN_EMULATOR_FTP_USER','XWN_EMULATOR_FTP_PASSWORD'],login.args):
    os.environ.setdefault(name,ast.literal_eval(arg))
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    write_json(dest,r)
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+6))
    try:f.connect('127.0.0.1',5248,timeout=f.budget());f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);return f
    except Exception:f.close();raise
deadline=time.monotonic()+60
while True:
    try:f=connect(deadline);break
    except ftplib.all_errors:
        if time.monotonic()>=deadline:raise
        time.sleep(1)
assert not (run/'cleanup.json').exists()
row=dict(cycle=1,status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe')
r['cycles'].append(row);save()
try:
    try:row.update(reply=f.sendcmd(row['command']),status='accepted')
    except ftplib.all_errors as exc:row.update(status='reply_uncertain',error=type(exc).__name__)
    save()
finally:f.close()
print('One joined-helper audio207 launch; never relaunch',flush=True)
deadline=time.monotonic()+1260;offline=False
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
