"""Run bounded private builds under the existing external build lease."""
import datetime,hashlib,json,os,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn526/build-supervisor001');out=K/'build-supervisor001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not out.exists() and not P.exists()
q=json.loads((K/'preflight001.json').read_bytes());assert q['passed'];P.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
 for n,h in q['inputs'].items():assert sha(Path(n))==h,n
verify();r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),lease_held=True,closed=True,passed=False,commands=[])
def save():out.write_bytes((json.dumps(r,indent=2)+'\n').encode())
save()
try:
 for name in ['build002.py','runner-build001.py','imports001.py']:
  verify();row=dict(source=name,closed=False);r['commands'].append(row);save()
  with (P/(name+'.stdout')).open('xb') as so,(P/(name+'.stderr')).open('xb') as se:
   try:
    p=subprocess.Popen(['python3','-B',str(K/name)],stdout=so,stderr=se,stdin=subprocess.DEVNULL);row['pid']=p.pid;save()
    try:code=p.wait(timeout=240)
    except subprocess.TimeoutExpired:
     row['timeout']=True;p.terminate()
     try:code=p.wait(timeout=3)
     except subprocess.TimeoutExpired:p.kill();code=p.wait(timeout=3);row['fallback_kill']=True
    row['exit_code']=code;row['closed']=p.poll() is not None;save();assert code==0 and not row.get('timeout'),name
   finally:
    if 'p' in locals() and p.poll() is None:p.kill();p.wait(timeout=3)
  verify()
 r['passed']=True
finally:r['closed']=all(x['closed'] for x in r['commands']);r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('PASS bounded wrapper/runner/import builds, all children closed')
