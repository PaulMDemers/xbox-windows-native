"""Actual500 controller paths; FTP, baseline, ownership and time modeled."""
import ftplib,hashlib,importlib.util,json,types
from pathlib import Path
K=Path(__file__).resolve().parent;ROOT=Path('C:/xwn500/host001');assert not ROOT.exists();ROOT.mkdir(parents=True)
spec=importlib.util.spec_from_file_location('controller500',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
stage497=json.loads((K.parent/'d3d-scene497/physical001-stage.json').read_text(encoding='utf-8'))
base={n:Path(stage497['before'][n]['path']).read_bytes() for n in [m.NORMAL,m.TARGET]}
base.update({n:b'explicit modeled mutable file '+n.encode() for n in m.MUTABLE})
binary=m.BUILD.read_bytes();good=Path('C:/xwn498/host001/case000.bin').read_bytes()
cases=['success','timeout','changed-normal','changed-target','changed-candidate','unknown-startup',
       *['existing-'+n for n in m.RECEIPTS],'unknown-owned-file','bad-pin','incomplete-stage',
       'short-entry','corrupt-entry','entry-only','final-close-unproved','five-receipts',
       'oversized-listing','oversized-transfer','listed-unreadable','transient-read','permanent-read',
       'pair-changed','observe-absent','observe-offline','observe-complete','observe-malformed',
       'stage-success','stage-existing','stage-readback-failure']
result=dict(passed=False,actual_controller=True,real_network=False,interfaces='FTP/baseline/ownership/time MODELED',cases=[])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 for case in cases:
  m.K=ROOT/case;m.K.mkdir();m.P=m.K/'private';state=dict(base);dirs={m.REMOTE};calls=[];reads={}
  state[m.REMOTE+'/default.xbe']=binary;state[m.REMOTE+'/owner.json']=b'modeled owner'
  m.ticket=lambda:None;m.baseline=lambda f,mode:None
  m.time=types.SimpleNamespace(monotonic=lambda:clock[0],sleep=lambda n:clock.__setitem__(0,clock[0]+n));clock=[0]
  def names(f,path):
   prefix=path+'/';rows={}
   for name in list(state)+list(dirs):
    if name.startswith(prefix):
     rest=name[len(prefix):];first=rest.split('/')[0]
     rows[first]=dict(directory='/' in rest or name in dirs,bytes=len(state.get(name,b'')))
   if case=='oversized-transfer' and path==m.REMOTE and 'entry.bin' in rows:rows['entry.bin']['bytes']=112
   return rows
  class F:
   def __enter__(self):self.sock=self;return self
   def __exit__(self,*args):return False
   def settimeout(self,n):assert n==20;calls.append(('timeout',n))
   def sendcmd(self,s):
    assert s==r'SITE EXEC E:\Applications\XWNBoot499a\default.xbe';calls.append(('SITE',s))
    if case=='timeout':raise TimeoutError('modeled uncertainty')
    return '200 EXEC command succeeded.'
   def mkd(self,path):assert path==m.REMOTE and path not in dirs;dirs.add(path);calls.append(('mkdir',path))
   def retrbinary(self,cmd,receive,chunk):
    assert cmd.startswith('RETR '+m.REMOTE+'/') and chunk==1024
    path=cmd[5:];calls.append(('receipt-read',path));reads[path]=reads.get(path,0)+1
    if case=='listed-unreadable':raise ftplib.error_perm('550 modeled read denial')
    data=state[path]
    if case=='pair-changed' and reads[path]%2==0:data=data[:-1]+bytes([data[-1]^1])
    for at in range(0,len(data),chunk):receive(data[at:at+chunk])
  f=F()
  def connect(**kw):
   assert kw.get('timeout') in (3,15)
   if case=='observe-offline' and observing[0]:raise TimeoutError('modeled offline')
   return f
  observing=[False];m.connect=connect;m.names=names
  collecting=[False];failures=[0]
  def get(f,path,optional=False):
   calls.append(('read',path))
   if collecting[0] and path==m.REMOTE+'/default.xbe' and case in ('transient-read','permanent-read') and (case=='permanent-read' or not failures[0]):
    failures[0]+=1;raise ftplib.error_perm('502 modeled transfer refusal')
   if optional:return state.get(path)
   return state[path]
  def put(f,path,data):
   assert path in (m.REMOTE+'/default.xbe',m.REMOTE+'/owner.json')
   assert path not in state;calls.append(('put',path));state[path]=data
   if case=='stage-readback-failure' and path.endswith('default.xbe'):state[path]+=b'bad'
  m.get=get;m.put=put
  package=dict(passed=True,candidate_sha256=hashlib.sha256(binary).hexdigest(),dependencies={str(K/'physical.py'):sha(K/'physical.py')})
  (m.K/'package001.json').write_text(json.dumps(package))
  if case.startswith('stage-'):
   if case!='stage-existing':
    dirs.clear();state.pop(m.REMOTE+'/owner.json');state.pop(m.REMOTE+'/default.xbe')
   try:m.stage();passed=True
   except AssertionError:passed=False
   assert passed==(case=='stage-success')
   r=json.loads((m.K/'physical001-stage.json').read_text());assert not r['temporary_hook_installed']
   assert all(n==m.REMOTE or n.startswith(m.REMOTE+'/') for n in r['writes'])
   if passed:
    assert len(r['before'])==10 and len(r['staged'])==2
    try:m.stage()
    except AssertionError:pass
    else:raise AssertionError('stage repeated')
   result['cases'].append(dict(case=case,stage_completed=passed,writes=r['writes']));continue
  m.P.mkdir()
  stage=dict(completed=True,temporary_hook_installed=False,return_plan='manual Windows normal restart; no auto hook',
             before={n:dict(sha256=hashlib.sha256(b).hexdigest()) for n,b in base.items()},
             staged={n:dict(sha256=hashlib.sha256(state[n]).hexdigest()) for n in (m.REMOTE+'/owner.json',m.REMOTE+'/default.xbe')})
  if case=='incomplete-stage':stage['completed']=False
  (m.K/'physical001-stage.json').write_text(json.dumps(stage))
  if case=='bad-pin':package['dependencies'][str(K/'physical.py')]='0'*64;(m.K/'package001.json').write_text(json.dumps(package))
  if case=='changed-normal':state[m.NORMAL]+=b'bad'
  if case=='changed-target':state[m.TARGET]+=b'bad'
  if case=='changed-candidate':state[m.REMOTE+'/default.xbe']+=b'bad'
  if case=='unknown-startup':state[m.START+'/other.cmd']=b'unknown'
  if case.startswith('existing-'):state[m.REMOTE+'/'+case[9:]]=b'old'
  if case=='unknown-owned-file':state[m.REMOTE+'/unexpected']=b'unknown'
  refused=case in cases[2:14]
  try:m.launch();launched=True
  except AssertionError:launched=False
  assert launched!=refused,(case,launched,refused)
  assert sum(x[0]=='SITE' for x in calls)==int(launched)
  if not launched:result['cases'].append(dict(case=case,launch_refused=True,site_count=0));continue
  before=len(calls)
  try:m.launch()
  except AssertionError:pass
  else:raise AssertionError('duplicate launch')
  assert len(calls)==before
  launch=json.loads((m.K/'physical001-launch.json').read_text());assert not launch['automatic_restart_installed']
  assert bool(launch.get('reply_uncertain'))==(case=='timeout')
  if case in ('entry-only','final-close-unproved','five-receipts','listed-unreadable','pair-changed','observe-complete'):state[m.REMOTE+'/entry.bin']=good
  if case in ('short-entry','observe-malformed'):state[m.REMOTE+'/entry.bin']=good[:100]
  if case=='corrupt-entry':state[m.REMOTE+'/entry.bin']=good[:-1]+bytes([good[-1]^1])
  if case=='five-receipts':
   for n in m.RECEIPTS[1:]:state[m.REMOTE+'/'+n]=b'explicit legacy receipt model '+n.encode()
  if case in ('oversized-listing','oversized-transfer'):state[m.REMOTE+'/entry.bin']=b'x'*4097
  if case.startswith('observe-'):
   observing[0]=True;m.observe();r=json.loads((m.K/'physical001-observation.json').read_text())
   assert r['completed'] and not r['windows_boot_proved']
   assert bool(r.get('deadline_reached'))==(case in ('observe-absent','observe-offline'))
   if case=='observe-complete':assert r['observations'][-1]['entry']['entry_state']=='complete'
   if case=='observe-malformed':assert r['observations'][-1]['entry']['entry_state']=='malformed'
   result['cases'].append(dict(case=case,observations=len(r['observations']),deadline=r.get('deadline_reached',False)));continue
  collecting[0]=True
  try:m.collect();collected=True
  except (AssertionError,ValueError,ftplib.error_perm):collected=False
  failed=case in ('oversized-listing','oversized-transfer','listed-unreadable','permanent-read','pair-changed')
  assert collected!=failed,(case,collected)
  r=json.loads((m.K/'physical001-collection.json').read_text());assert r['remote_writes']==[] and r['owned_hook_never_installed']
  assert r['completed']==collected and not r['normal_windows_shutdown_proved']
  if case=='permanent-read':assert failures[0]==2 and len(r['read_failures'])==2
  if case=='transient-read':assert failures[0]==1 and len(r['read_failures'])==1
  if case=='listed-unreadable':assert len(r['read_failures'])==2 and m.REMOTE+'/entry.bin' not in r['files']
  if collected:
   assert len(r['files'])==17
   expected='complete' if case in ('entry-only','final-close-unproved','five-receipts') else 'malformed' if case in ('short-entry','corrupt-entry') else 'absent_in_listing'
   assert r['entry']['entry_state']==expected
   if expected=='complete':assert not r['entry']['final_close_proved'] and not r['entry']['windows_boot_proved']
  before=len(calls)
  try:m.collect()
  except AssertionError:pass
  else:raise AssertionError('collection repeated')
  assert len(calls)==before
  assert all(state[n]==b for n,b in base.items())
  result['cases'].append(dict(case=case,collection_completed=collected,site_count=1,read_failures=len(r.get('read_failures',[]))))
 result.update(passed=True,case_count=len(cases),source_sha256=sha(K/'physical.py'),decoder_sha256=sha(K.parent/'entry-receipt498/decode.py'))
except BaseException as e:result['error']=repr(e);raise
finally:
 result['private_files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in ROOT.rglob('*') if p.is_file()}
 (K/'host001.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print('PASS actual controller cases:',len(cases))
