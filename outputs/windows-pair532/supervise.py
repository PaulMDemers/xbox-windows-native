"""Bounded owned controller lifetime. Never retries an action or remote launch."""
import datetime,importlib.util,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
s=importlib.util.spec_from_file_location('atomic532',W/'outputs/surface-bridge260/atomic_json.py')
atomic=importlib.util.module_from_spec(s);s.loader.exec_module(atomic)
LOG=Path('C:/xwn532/supervisor001')
LIMITS=dict(before=240,launch1=120,launch2=120,after1=240,after2=240)
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def run(action):
 assert action in LIMITS
 out=K/('supervisor-'+action+'.json');folder=LOG/action
 assert not out.exists() and not folder.exists()
 folder.mkdir(parents=True)
 r=dict(action=action,started_utc=utc(),child_started=False,closed=True,completed=False,
        timeout_seconds=LIMITS[action],deadline_reached=False,remote_retry_allowed=False,
        console_state='unknown until actual controller/cold evidence; host exit is not console exit')
 def save():
  # Parent record is independent of child evidence; atomic replace, no remote action.
  atomic.write_json(out,r)
 save();p=None
 try:
  env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
  with (folder/'stdout.txt').open('xb') as stdout,(folder/'stderr.txt').open('xb') as stderr:
   p=subprocess.Popen([sys.executable,'-B',str(K/'controller.py'),action],cwd=W,
                      env=env,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
   r.update(child_started=True,pid=p.pid,closed=False);save()
   try:code=p.wait(timeout=LIMITS[action])
   except subprocess.TimeoutExpired:
    r['deadline_reached']=True;p.terminate()
    try:code=p.wait(timeout=3)
    except subprocess.TimeoutExpired:p.kill();code=p.wait(timeout=3);r['fallback_kill']=True
   r.update(exit_code=code,closed=p.poll() is not None,completed=code==0 and not r['deadline_reached'])
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:
  if p is not None and p.poll() is None:
   p.terminate()
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=3)
  r['closed']=p is None or p.poll() is not None;r['finished_utc']=utc();save()
 return r
if __name__=='__main__':
 assert len(sys.argv)==2
 r=run(sys.argv[1]);print(json.dumps(r));sys.exit(0 if r['completed'] else 1)
