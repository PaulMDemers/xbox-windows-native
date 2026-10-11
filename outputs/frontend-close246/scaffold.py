"""New246 kit; never copy actual run outcomes or relaunch an old child."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-lifecycle245';ws=k.parents[1]
names=['audit-emulator.py','close-host.py','common.py','parsing.py','preservation.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Invoke-245.ps1','matrix.py','trace.py','freeze.py','test-close.py','test-connection.py','test-guards003.py','schema.py','test-pair.py','lifecycle.py','test-lifecycle.py','analyze-lifecycle002.py']
for name in names:
 p=k/name.replace('Invoke-245','Invoke-246');assert not p.exists()
 s=(old/name).read_text().replace('gpu-lifecycle245','frontend-close246').replace('phase245','phase246').replace('Invoke-245','Invoke-246')
 if name=='Run.ps1':s=s.replace('build005','build001').replace('xemu-lifecycle244.exe','xemu-frontend246.exe')
 if name=='freeze.py':
  s=s.replace("k.parent/'gpu-lifecycle244/emulator-frozen.json'","k.parent/'gpu-lifecycle245/emulator-frozen.json'").replace('artifacts/build005','artifacts/build001')
 if name=='trace.py':
  s=s.replace('quarantined=False','quarantined=False\nfrontend_requested=False;frontend_reopened=False',1)
  anchor=' # Existing CPU-exclusive queue may run while stopped. No wait under actor locks.'
  assert anchor in s;s=s.replace(anchor,''' # Close actual UI admission at pinned FreeLoader; no synchronous QOM wait.
 frontend_requested=True
 r['frontend_close_request_may_be_accepted']=True;save()
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close true');assert 'Error' not in reply
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report')
  state=int(re.search(r'(?<![a-z_])state=(\\d+)',reply)[1])
  if state in [2,3]:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['frontend_closed_report']=reply;save()
 assert state==2,'Explicit bounded UI close refusal, never retry'
 assert ' loan=0 ' in reply and ' bql=0 ' in reply and ' error=0 ' in reply
 # No new frame may start throughout this interval. Keep all shared objects.
 time.sleep(.2)
 r['frontend_closed_reread']=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report');save()
 assert r['frontend_closed_reread']==reply
 reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close false');assert 'Error' not in reply
 frontend_reopened=True;r['frontend_reopen_requested']=True;save()
 deadline=time.monotonic()+8
 while True:
  reply=cmd('qom-get '+r['nv2a_qom_path']+' xwn-frontend246-report')
  state=int(re.search(r'(?<![a-z_])state=(\\d+)',reply)[1])
  if state==5:break
  assert time.monotonic()<deadline;time.sleep(.025)
 r['frontend_reopened_report']=reply;r['frontend_scope_passed']=True;save()
''' + anchor)
  anchor=' if g:\n  if not stopped:'
  assert anchor in s;s=s.replace(anchor,''' if frontend_requested and not frontend_reopened:
  try:
   reply=cmd('qom-set '+r['nv2a_qom_path']+' xwn-frontend246-close false')
   r['frontend_failure_reopen_reply']=reply;frontend_reopened='Error' not in reply
   if not frontend_reopened:quarantined=True
  except Exception as exc:r['frontend_failure_reopen_error']=repr(exc);quarantined=True
 if g:
  if not stopped:''')
 if name=='audit-emulator.py':
  s=s.replace("r['publication_limit']=", "r['frontend_scope_passed']=r['guest_trace_scope_passed'] and r['handoff_trace'].get('frontend_scope_passed',False)\nr['publication_limit']=")
 p.write_text(s)
for name in ['fixture-preserve001.json','inventory001.json','inventory.c']:
 shutil.copyfile(old/name,k/name)
p=k/'fixture-preserve001.json';d=json.loads(p.read_text());d['new_unique_runtime']='nt5-phase246-preserve001';d['compiled_emulator_from']='outputs/frontend-close246/build001.json';p.write_text(json.dumps(d,indent=2)+'\n')
for name in ['inputs','ram-source']:shutil.copytree(old/'artifacts'/name,k/'artifacts'/name)
(k/'preserve001/artifacts').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
for row in json.loads((old/'baseline-inputs001.json').read_text())['files']:
 p=ws/row['path'];assert sha(p)==row['sha256'];to=k/'preserve001/artifacts'/p.name;shutil.copyfile(p,to);rows.append(dict(path=to.relative_to(ws).as_posix(),sha256=sha(to)))
(k/'baseline-inputs001.json').write_text(json.dumps(dict(passed=True,files=rows,physical_access=False),indent=2)+'\n')
print('246 fresh scaffolding/baseline prepared; no guest launched')
