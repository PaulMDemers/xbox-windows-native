"""Model actual assets-only move, hook-last staging, single launch and hook-first cleanup."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller590test',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=c.read;sha=c.m.sha;keep=c.m.keep;cases=[]
class FTP:
 def __init__(self,mode):self.files={n:b'baseline' for n in c.FILES};self.files[c.m.NORMAL]=b'normal';self.files[c.m.TARGET]=b'target';self.files['/E/winnt/system32/kernel32.dll']=b'module';self.files['/E/xwn582-kit/owner.json']=b'priorowner';self.dirs={'/E/xwn582-kit','/E/xwn582-kit/game'};self.calls=[];self.mode=mode;self.sock=self
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def settimeout(self,n):assert n==20
 def sendcmd(self,command):
  assert command==c.pair.COMMAND and read(c.K/'launch001.json')['requested'];self.calls.append(('launch',command))
  if self.mode=='uncertain':raise TimeoutError()
  return '200 modeled'
 def mkd(self,n):assert n not in self.dirs;self.dirs.add(n);self.calls.append(('mkdir',n))
 def rename(self,a,b):
  self.calls.append(('rename',a,b))
  if a==c.HOOK:assert b==c.USED and b not in self.files;self.files[b]=self.files.pop(a);return
  assert a=='/E/xwn582-kit/game' and b==c.KIT+'/game' and b not in self.dirs
  if self.mode=='rename-error':raise TimeoutError('Modeled rename error; no retry')
  for n in list(self.files):
   if n.startswith(a+'/'):self.files[b+n[len(a):]]=self.files.pop(n)
  for n in list(self.dirs):
   if n==a or n.startswith(a+'/'):self.dirs.remove(n);self.dirs.add(b+n[len(a):])
def names(f,p):
 rows={}
 for n in set(f.files)|f.dirs:
  if n.startswith(p+'/'):
   tail=n[len(p)+1:];name=tail.split('/')[0];rows[name]=dict(directory='/' in tail or n in f.dirs,bytes=len(f.files.get(n,b'')))
 return rows
def get(f,n,optional=False):return f.files.get(n) if optional else f.files[n]
def put(f,n,b):
 f.files[n]=b;f.calls.append(('put',n))
 if f.mode=='corrupt-runner' and n.endswith('/run589.exe'):f.files[n]+=b'bad'
with tempfile.TemporaryDirectory(prefix='xwn590-model-') as tmp:
 for mode in ['pass','uncertain','changed-old-asset','extra-old-file','existing-kit','low-space','rename-error','corrupt-runner','changed-stage','extra-startup','new-save']:
  c.K=Path(tmp)/mode;c.K.mkdir();c.P=c.K/'private';f=FTP(mode);files={}
  for name,b in [('game/RCT.EXE',b'pristinegame'),('game/Data/Game.cfg',b'pristinecfg'),('run589.exe',b'runner')]:
   p=c.K/'payload'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);files[name]=dict(path=str(p),bytes=len(b),sha256=sha(b))
  f.dirs.add('/E/xwn582-kit/game/Data');f.files['/E/xwn582-kit/game/RCT.EXE']=b'pristinegame';f.files['/E/xwn582-kit/game/Data/Game.cfg']=b'oldcfg'
  expected={n[len('/E/xwn582-kit/game/'):]:dict(bytes=len(b),sha256=sha(b)) for n,b in f.files.items() if n.startswith('/E/xwn582-kit/game/')}
  q=dict(files=files,reuse_expected=expected,restore_assets=['Data/Game.cfg'],previous_owner_sha256=sha(b'priorowner'),runtime_module_pins={'kernel32.dll':sha(b'module')})
  (c.K/'package001.json').write_text('{}');(c.K/'console-space001.json').write_text(json.dumps(dict(admitted=mode!='low-space',projected_remaining_bytes=1024**3)))
  c.verify=lambda:q;c.boot_work_closed=lambda:None;c.budget=lambda:None;c.m.connect=lambda **kw:f;c.m.baseline=lambda *a:None;c.m.names=names;c.m.get=get;c.m.put=put;c.m.keep=keep;c.m.cold_pair=lambda n,r,o:get(f,n,True)
  def startup(f,armed):
   assert f.files[c.m.NORMAL]==b'normal' and f.files[c.m.TARGET]==b'target'
   rows=names(f,c.m.START);assert set(rows)<={'xwnsetup.cmd','desktop.ini'}|({'xwn590.cmd'} if armed else set())
   if armed:assert f.files[c.HOOK]==c.hook()
   return rows
  c.startup=startup
  if mode=='changed-old-asset':f.files['/E/xwn582-kit/game/RCT.EXE']+=b'bad'
  if mode=='extra-old-file':f.files['/E/xwn582-kit/game/unexpected']=b'unknown'
  if mode=='existing-kit':f.dirs.add(c.KIT)
  try:c.stage();staged=True
  except (AssertionError,TimeoutError):staged=False
  assert staged==(mode in ['pass','uncertain','changed-stage','extra-startup','new-save']),mode
  if not staged:
   assert c.HOOK not in f.files and not any(x[0]=='launch' for x in f.calls)
   cases.append(dict(case=mode,refused_before_hook=True));continue
  assert [x for x in f.calls if x[0]=='put'][-1]==('put',c.HOOK)
  assert f.files[c.KIT+'/game/Data/Game.cfg']==b'pristinecfg' and f.files['/E/xwn582-kit/owner.json']==b'priorowner'
  prior=len(f.calls)
  try:c.stage()
  except AssertionError:pass
  else:raise AssertionError('Repeated stage admitted')
  assert len(f.calls)==prior
  if mode=='changed-stage':f.files[c.KIT+'/game/RCT.EXE']+=b'bad'
  if mode=='extra-startup':f.files[c.m.START+'/unknown.cmd']=b'bad'
  try:c.launch();launched=True
  except AssertionError:launched=False
  assert launched==(mode in ['pass','uncertain','new-save']),mode
  if not launched:cases.append(dict(case=mode,launch_refused=True));continue
  assert sum(x[0]=='launch' for x in f.calls)==1
  try:c.launch()
  except AssertionError:pass
  else:raise AssertionError('Repeated launch admitted')
  assert sum(x[0]=='launch' for x in f.calls)==1
  assert bool(read(c.K/'launch001.json').get('reply_uncertain'))==(mode=='uncertain')
  f.dirs.add(c.RESULT);f.files[c.RESULT+'/runner.txt']=b'modeled receipt'
  if mode=='new-save':f.files[c.KIT+'/game/new.SV4']=b'newsave'
  f.calls=[];c.collect();col=read(c.K/'collection001.json')
  assert col['completed'] and col['hook_removed'] and f.calls[0]==('rename',c.HOOK,c.USED)
  if mode=='new-save':assert col['files'][c.KIT+'/game/new.SV4']['sha256']==sha(b'newsave')
  cases.append(dict(case=mode,assets_only_move=True,pristine_restore=True,hook_last=True,one_launch=True,hook_first=True))
out=K/'controller-host003.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,cases=cases,source_sha256=hashlib.sha256((K/'controller001.py').read_bytes()).hexdigest(),scope='Transport/evidence fault models only; no real console access or game execution'),indent=2)+'\n');print('Passed',len(cases),'controller cases')
