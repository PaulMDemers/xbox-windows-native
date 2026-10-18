"""Actual controller functions; all FTP, baseline checks and elapsed time MODELED."""
import ftplib,hashlib,importlib.util,json,sys,types
from pathlib import Path
K=Path(__file__).resolve().parent;ROOT=Path('C:/xwn518/controller-host001')
assert not ROOT.exists();ROOT.mkdir(parents=True)
sys.path.insert(0,str(K));spec=importlib.util.spec_from_file_location('controller518',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=json.loads((K.parent/'physical-busy472/stage001.json').read_text(encoding='utf-8'))
base={n:Path(old['before'][n]['path']).read_bytes() for n in [m.NORMAL,m.TARGET]}
base.update({n:b'modeled unchanged mutable file' for n in m.MUTABLE})
xbe=m.BUILD.read_bytes();receipt=Path('C:/xwn517/cold001/entry.bin').read_bytes()
original_usage=m.shutil.disk_usage;original_time=m.time;cases=[]
def refuses(call,errors=(AssertionError,ValueError,ftplib.Error,OSError)):
 try:call()
 except errors:return True
 raise AssertionError('negative accepted')
def setup(name):
 global state,calls,clock,readfail
 m.K=ROOT/name;m.K.mkdir();m.P=m.K/'private'
 for n in ['physical.py','entry_decode.py']:(m.K/n).write_bytes((K/n).read_bytes())
 (m.K/'package001.json').write_bytes(b'{}')
 state=dict(base);calls=[];clock=[0.0];readfail=[0]
 class F:
  def __enter__(self):self.sock=self;return self
  def __exit__(self,*args):return False
  def settimeout(self,n):assert n==20;calls.append(('timeout',n))
  def mkd(self,n):assert n==m.REMOTE;calls.append(('mkdir',n))
  def sendcmd(self,s):
   calls.append(('SITE',s));assert s==r'SITE EXEC E:\Applications\XWNBoot516a\default.xbe'
   if name=='launch-uncertain':raise TimeoutError('modeled accepted-but-reply-lost')
   return '200 EXEC command succeeded.'
  def retrbinary(self,cmd,receive,chunk):
   assert chunk==1024;calls.append(('RETR',cmd[5:]))
   if name=='observe-listed-unreadable':raise ftplib.error_perm('550 modeled listed file unreadable')
   data=state[cmd[5:]]
   for i in range(0,len(data),chunk):receive(data[i:i+chunk])
 f=F()
 def names(f,path):
  result={};prefix=path+'/'
  for n,b in state.items():
   if n.startswith(prefix):
    rest=n[len(prefix):];first=rest.split('/')[0];result[first]=dict(directory='/' in rest,bytes=len(b))
  return result
 def get(f,n,optional=False):
  calls.append(('get',n))
  assert n.startswith('/E/'),'console C access'
  if name in ('cold-transient','cold-permanent') and n==m.REMOTE+'/default.xbe' and (m.K/'physical001-collection.json').exists():
   if name=='cold-permanent' or readfail[0]==0:readfail[0]+=1;raise ftplib.error_perm('502 modeled data refusal')
  return state.get(n) if optional else state[n]
 def put(f,n,b):assert n.startswith(m.REMOTE+'/');calls.append(('put',n));state[n]=b
 def connect(**kw):
  if name=='observe-offline' and (m.K/'physical001-launch.json').exists():raise ConnectionRefusedError('modeled offline')
  return f
 m.connect=connect;m.names=names;m.get=get;m.put=put;m.baseline=lambda f,mode:None;m.verify=lambda:xbe
 m.time=types.SimpleNamespace(monotonic=lambda:clock[0],sleep=lambda n:clock.__setitem__(0,clock[0]+n))
 m.shutil.disk_usage=lambda p:types.SimpleNamespace(free=30*1024**3)
 return f
names_cases=['success','launch-uncertain','stage-existing','stage-low-space','stage-unknown-startup','stage-changed-launcher','launch-changed-launcher','launch-changed-normal','launch-changed-mutable','launch-changed-candidate','launch-changed-owner','launch-unknown-startup','launch-entry','launch-report','launch-refusal','launch-handoff','launch-context','launch-witness','launch-unknown','launch-directory','observe-absent','observe-offline','observe-malformed','observe-listed-unreadable','observe-oversize','cold-transient','cold-permanent','cold-changed','collect-startup-changed']
for name in names_cases:
 f=setup(name)
 if name=='stage-existing':state[m.REMOTE+'/old.bin']=b'x'
 if name=='stage-low-space':m.shutil.disk_usage=lambda p:types.SimpleNamespace(free=20*1024**3)
 if name=='stage-unknown-startup':state[m.START+'/other.cmd']=b'x'
 if name=='stage-changed-launcher':state[m.TARGET]+=b'x'
 if name.startswith('stage-'):
  refuses(m.stage);assert not any(c[0] in ('put','mkdir','SITE') for c in calls);cases.append(dict(case=name,refused_before_write=True));continue
 m.stage();s=m.read(m.K/'physical001-stage.json');assert s['completed'] and not s['temporary_startup_added']
 assert s['physical_writes']==[m.REMOTE,m.REMOTE+'/owner.json',m.REMOTE+'/default.xbe']
 refuses(m.stage)
 changes={'launch-changed-launcher':m.TARGET,'launch-changed-normal':m.NORMAL,'launch-changed-mutable':m.MUTABLE[0],'launch-changed-candidate':m.REMOTE+'/default.xbe','launch-changed-owner':m.REMOTE+'/owner.json'}
 if name in changes:state[changes[name]]+=b'x'
 if name=='launch-unknown-startup':state[m.START+'/other.cmd']=b'x'
 for r in ['entry','report','refusal','handoff','context','witness','unknown']:
  if name=='launch-'+r:state[m.REMOTE+'/'+r+'.bin']=b'x'
 if name=='launch-directory':state[m.REMOTE+'/sub/file']=b'x'
 if name.startswith('launch-') and name!='launch-uncertain':
  refuses(m.launch);assert not any(c[0]=='SITE' for c in calls);cases.append(dict(case=name,refused_before_SITE=True));continue
 m.launch();refuses(m.launch);assert sum(c[0]=='SITE' for c in calls)==1
 launched=m.read(m.K/'physical001-launch.json');assert bool(launched.get('reply_uncertain'))==(name=='launch-uncertain')
 assert not launched['windows_boot_intended'] and not launched['automatic_restart_installed']
 if name not in ('observe-absent','observe-offline'):state[m.REMOTE+'/entry.bin']=receipt
 if name=='observe-malformed':state[m.REMOTE+'/entry.bin']=b'bad'
 if name=='observe-oversize':state[m.REMOTE+'/entry.bin']=b'x'*4097
 if name in ('observe-oversize','observe-listed-unreadable'):
  refuses(m.observe);r=m.read(m.K/'physical001-observation.json');assert not r['completed'] and r['receipt_transport_failed'];cases.append(dict(case=name,transport_refusal=True));continue
 m.observe();refuses(m.observe);observed=m.read(m.K/'physical001-observation.json');assert observed['completed']
 if name in ('observe-absent','observe-offline'):
  assert observed['deadline_reached'] and len(observed['observations'])==18
  if name=='observe-offline':cases.append(dict(case=name,bounded_unknown=True));continue
 if name=='observe-malformed':assert observed['entry']['entry_state']=='malformed'
 if name=='collect-startup-changed':state[m.START+'/other.cmd']=b'x';refuses(m.collect);cases.append(dict(case=name,refused=True));continue
 if name=='cold-changed':
  oldget=m.get;counter=[0]
  def changing(f,n,optional=False):
   b=oldget(f,n,optional)
   if n==m.MUTABLE[0]:counter[0]+=1;return b+str(counter[0]).encode()
   return b
  m.get=changing;refuses(m.collect);cases.append(dict(case=name,refused=True));continue
 if name=='cold-permanent':
  refuses(m.collect);assert readfail[0]==2;assert not m.read(m.K/'physical001-collection.json')['completed'];cases.append(dict(case=name,read_attempts=2));continue
 m.collect();refuses(m.collect);c=m.read(m.K/'physical001-collection.json');assert c['completed'] and c['remote_writes']==[] and not c['temporary_hook_installed']
 assert all(c['files'][n]['unchanged'] for n in [*s['before'],*s['staged']])
 if name=='cold-transient':assert readfail[0]==1 and len(c['read_failures'])==1
 if name not in ('observe-malformed','observe-absent'):assert c['entry']['entry_execution'] and not c['entry']['final_close_proved']
 assert all(state[n]==b for n,b in base.items());cases.append(dict(case=name,complete=True,site_requests=1))
m.shutil.disk_usage=original_usage;m.time=original_time
r=dict(passed=True,cases=cases,actual_stage_launch_observe_collect=True,FTP_baseline_clock='MODELED',no_physical_access=True,source_sha256=hashlib.sha256((K/'physical.py').read_bytes()).hexdigest())
(K/'controller-host001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PASS',len(cases),'actual controller cases with modeled FTP/baseline/time')
