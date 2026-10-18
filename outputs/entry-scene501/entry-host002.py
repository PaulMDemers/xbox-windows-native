"""Actual combined dispatcher; FTP, ticket, baseline and elapsed time modeled."""
import ftplib,hashlib,importlib.util,json,sys,types
from pathlib import Path
K=Path(__file__).resolve().parent;ROOT=Path('C:/xwn501/entry-host002');assert not ROOT.exists();ROOT.mkdir(parents=True)
sys.path.insert(0,str(K));spec=importlib.util.spec_from_file_location('entry501',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((K.parent/'d3d-scene497/physical001-stage.json').read_text())
base={n:Path(old['before'][n]['path']).read_bytes() for n in [m.NORMAL,m.TARGET]}
base.update({n:b'modeled mutable '+n.encode() for n in m.MUTABLE})
good=Path('C:/xwn498/host001/case000.bin').read_bytes();binary=m.BUILD.read_bytes()
cases=[*['existing-'+n for n in m.RECEIPTS],'unknown-owned','complete','short','corrupt','five',
 'oversized-listing','oversized-transfer','unreadable','changed-pair',
 'observe-complete','observe-short','observe-absent','observe-offline','observe-unreadable','observe-oversized',
 'stage-success','stage-existing','stage-readback-failure']
r=dict(passed=False,actual_controller=True,interfaces='FTP/ticket/baseline/elapsed time MODELED',real_network=False,cases=[])
try:
 for case in cases:
  m.K=ROOT/case;m.K.mkdir();m.P=m.K/'private';state=dict(base);dirs={m.REMOTE};calls=[];reads={};clock=[0]
  state.update({m.HOOK:m.hook(),m.REMOTE+'/owner.json':b'model owner',m.REMOTE+'/default.xbe':binary})
  m.ticket=lambda:None;m.baseline=lambda f,mode:None
  m.time=types.SimpleNamespace(monotonic=lambda:clock[0],sleep=lambda n:clock.__setitem__(0,clock[0]+n))
  def names(f,path):
   rows={};prefix=path+'/'
   for n in list(state)+list(dirs):
    if n.startswith(prefix):
     rest=n[len(prefix):];rows[rest.split('/')[0]]=dict(directory='/' in rest or n in dirs,bytes=len(state.get(n,b'')))
   if case=='oversized-transfer' and path==m.REMOTE and 'entry.bin' in rows:rows['entry.bin']['bytes']=112
   return rows
  class F:
   def __enter__(self):self.sock=self;return self
   def __exit__(self,*args):return False
   def settimeout(self,n):assert n==20
   def sendcmd(self,s):assert s==r'SITE EXEC E:\Applications\XWNBoot499a\default.xbe';calls.append(('SITE',s));return '200 EXEC accepted'
   def rename(self,a,b):assert a==m.HOOK and b not in state;calls.append(('rename',a,b));state[b]=state.pop(a)
   def mkd(self,p):assert p in (m.REMOTE,m.KITROOT) and p not in dirs;dirs.add(p);calls.append(('mkdir',p))
   def retrbinary(self,cmd,receive,chunk):
    assert chunk==1024;path=cmd[5:];assert path.startswith(m.REMOTE+'/');reads[path]=reads.get(path,0)+1
    if case in ('unreadable','observe-unreadable'):raise ftplib.error_perm('550 modeled listed file read failure')
    data=state[path]
    if case=='changed-pair' and reads[path]%2==0:data=data[:-1]+bytes([data[-1]^1])
    for j in range(0,len(data),chunk):receive(data[j:j+chunk])
  f=F();observing=[False]
  def connect(**kw):
   if case=='observe-offline' and observing[0]:raise TimeoutError('modeled offline')
   return f
  def put(f,p,b):
   assert p not in state and (p.startswith(m.REMOTE+'/') or p.startswith(m.KITROOT+'/') or p==m.HOOK)
   calls.append(('put',p));state[p]=b
   if case=='stage-readback-failure' and p.endswith('default.xbe'):state[p]+=b'changed'
  m.connect=connect;m.names=names;m.get=lambda f,p,optional=False:state.get(p) if optional else state[p];m.put=put
  package=dict(passed=True,dependencies={str(K/'physical.py'):sha(K/'physical.py')},files={'default.xbe':dict(path=str(m.BUILD),sha256=sha(m.BUILD))},runtime_module_pins={})
  (m.K/'package001.json').write_text(json.dumps(package))
  if case.startswith('stage-'):
   state.pop(m.HOOK)
   if case!='stage-existing':dirs.clear();state.pop(m.REMOTE+'/owner.json');state.pop(m.REMOTE+'/default.xbe')
   for p in K.glob('*.py'):(m.K/p.name).write_bytes(p.read_bytes())
   (m.K/'launcher-input.json').write_bytes((K/'launcher-input.json').read_bytes())
   try:m.stage();ok=True
   except AssertionError:ok=False
   assert ok==(case=='stage-success')
   result=json.loads((m.K/'physical001-stage.json').read_text());assert result['completed']==ok
   if ok:
    assert calls[-1]==('put',m.HOOK) and result['temporary_startup_added'] and len(result['before'])==10
   else:assert m.HOOK not in state
   r['cases'].append(dict(case=case,completed=ok,writes=calls));continue
  m.P.mkdir();stage=dict(completed=True,source_pins={},before={n:dict(sha256=hashlib.sha256(b).hexdigest()) for n,b in base.items()},staged={n:dict(sha256=hashlib.sha256(state[n]).hexdigest()) for n in (m.REMOTE+'/owner.json',m.REMOTE+'/default.xbe')})
  (m.K/'physical001-stage.json').write_text(json.dumps(stage))
  if case.startswith('existing-'):state[m.REMOTE+'/'+case[9:]]=b'preexisting'
  if case=='unknown-owned':state[m.REMOTE+'/unknown']=b'unknown'
  try:m.launch();launched=True
  except AssertionError:launched=False
  refused=case.startswith('existing-') or case=='unknown-owned';assert launched!=refused
  assert sum(x[0]=='SITE' for x in calls)==int(launched)
  if refused:r['cases'].append(dict(case=case,launch_refused=True));continue
  try:m.launch()
  except AssertionError:pass
  else:raise AssertionError('duplicate accepted request')
  assert len(calls)==1
  if case not in ('observe-absent','observe-offline'):state[m.REMOTE+'/entry.bin']=good
  if case in ('short','observe-short'):state[m.REMOTE+'/entry.bin']=good[:100]
  if case=='corrupt':state[m.REMOTE+'/entry.bin']=good[:-1]+bytes([good[-1]^1])
  if case in ('oversized-listing','oversized-transfer','observe-oversized'):state[m.REMOTE+'/entry.bin']=b'x'*4097
  if case=='five':
   for n in m.RECEIPTS[1:]:state[m.REMOTE+'/'+n]=b'modeled invalid legacy receipt'
  if case.startswith('observe-'):
   observing[0]=True
   try:m.observe();ok=True
   except (AssertionError,ValueError,ftplib.Error):ok=False
   expected=case not in ('observe-unreadable','observe-oversized');assert ok==expected
   result=json.loads((m.K/'physical001-observation.json').read_text())
   if expected:
    assert result['completed']
    assert bool(result.get('deadline_reached'))==(case in ('observe-absent','observe-offline'))
   else:assert result['receipt_transport_failed'] and not result['completed']
   r['cases'].append(dict(case=case,completed=ok,observations=len(result['observations'])));continue
  try:m.collect();ok=True
  except (AssertionError,ValueError,ftplib.Error):ok=False
  expected=case not in ('oversized-listing','oversized-transfer','unreadable','changed-pair');assert ok==expected
  result=json.loads((m.K/'physical001-collection.json').read_text());assert result['hook_removed'] and m.HOOK not in state
  assert calls[1][0]=='rename' and result['completed']==ok
  if ok:
   assert len(result['files'])==18
   assert result['entry']['entry_state']==('malformed' if case in ('short','corrupt') else 'complete')
   if result['entry']['entry_execution']:assert not result['entry']['windows_boot_proved'] and not result['entry']['final_close_proved']
  assert all(state[n]==b for n,b in base.items())
  r['cases'].append(dict(case=case,collected=ok,hook_removed=True))
 r.update(passed=True,case_count=len(cases),source_sha256=sha(K/'physical.py'))
except BaseException as e:r['error']=repr(e);raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in ROOT.rglob('*') if p.is_file()}
 (K/'entry-host002.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
print('PASS',len(cases),'combined controller paths; remote interfaces modeled')
