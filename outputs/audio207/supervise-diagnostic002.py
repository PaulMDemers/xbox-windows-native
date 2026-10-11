"""Diagnostic single launch followed by paused read-only guest state observation."""
import datetime,ftplib,json,os,subprocess,sys,time
from pathlib import Path
os.environ['PYTHONPATH']='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages'
sys.path.insert(0,os.environ['PYTHONPATH'])
from PIL import Image
import PIL._imaging
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['diagnostic002'];out=k/case;run=ws/('work/runs/nt5-audio207-'+case)
sys.path.insert(0,str(k.parent/'gpu-reset-banner152'));from ftp_deadline import DeadlineFTP
dest=out/'launch.json';assert not dest.exists() and (run/'instance.json').exists() and not (run/'cleanup.json').exists()
r=dict(run=run.name,host='127.0.0.1',port=4696,debugger=False,physical_access=False,cycles=[])
# Recover only the documented local fixture defaults; never read console config.
import ast
tree=ast.parse((k.parent/'native-windows-prebuild/launch_unleashx.py').read_text())
login=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='login')
for name,arg in zip(['XWN_EMULATOR_FTP_USER','XWN_EMULATOR_FTP_PASSWORD'],login.args):
    os.environ.setdefault(name,ast.literal_eval(arg))
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save():
    temp=dest.with_suffix('.tmp');temp.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');temp.replace(dest)
def connect(deadline):
    f=DeadlineFTP(min(deadline,time.monotonic()+6))
    try:f.connect('127.0.0.1',4696,timeout=f.budget());f.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD']);return f
    except Exception:f.close();raise
deadline=time.monotonic()+60
while True:
    try:f=connect(deadline);break
    except ftplib.all_errors:
        if time.monotonic()>=deadline:raise
        time.sleep(1)
assert not (run/'cleanup.json').exists()
row=dict(cycle=1,status='requesting',launch_requested_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe')
r['cycles'].append(row);save()
try:
    try:row.update(reply=f.sendcmd(row['command']),status='accepted')
    except ftplib.all_errors as exc:row.update(status='reply_uncertain',error=type(exc).__name__)
    save()
finally:f.close()
print('One diagnostic launch; never relaunch',flush=True)

r['diagnostic_only']=True; r['ordinary_qualification']=False; save()
deadline=time.monotonic()+175
while time.monotonic()<deadline:
    if (run/'cleanup.json').exists():raise RuntimeError('Runner closed before diagnostic observation')
    time.sleep(2)
for script,args in [('native-windows-prebuild/monitor_capture.py',['--output',str(run/'diagnostic-screen.png'),'--auto-framebuffer']),('native-windows-nt5-kernel/capture-runtime.py',['--output',str(run/'diagnostic-state.json')])]:
    p=subprocess.run([sys.executable,str(k.parent/script),'--port','4694']+args,capture_output=True,text=True)
    (run/(Path(script).stem+'-diagnostic.log')).write_text(p.stdout+'\n'+p.stderr)
    r.setdefault('observations',[]).append(dict(script=script,exit=p.returncode,utc=utc()));save()
r['status']='diagnostic_observations_complete_owned_host_stop_requested';save()
(run/'capture-complete.signal').touch(exist_ok=False)
print(r['status'],flush=True)
