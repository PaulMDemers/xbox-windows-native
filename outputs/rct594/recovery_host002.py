"""Model actual assets-only move, hook-last staging, single launch and hook-first cleanup."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller594recoverytest',K/'controller003.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=c.read;sha=c.m.sha;keep=c.m.keep;cases=[]
class FTP:
 def __init__(self,mode):self.files={n:b'baseline' for n in c.FILES};self.files[c.m.NORMAL]=b'normal';self.files[c.m.TARGET]=b'target';self.files['/E/winnt/system32/kernel32.dll']=b'module';self.files['/E/xwn586-kit/owner.json']=b'priorowner';self.dirs={'/E/xwn586-kit','/E/xwn586-kit/game'};self.calls=[];self.mode=mode;self.sock=self
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def close(self):pass
 def settimeout(self,n):assert n==20
 def sendcmd(self,command):
  assert command==c.pair.COMMAND and read(c.K/'launch001.json')['requested'];self.calls.append(('launch',command))
  if self.mode=='uncertain':raise TimeoutError()
  return '200 modeled'
 def mkd(self,n):assert n not in self.dirs;self.dirs.add(n);self.calls.append(('mkdir',n))
 def rename(self,a,b):
  self.calls.append(('rename',a,b))
  if a==c.HOOK:assert b==c.USED and b not in self.files;self.files[b]=self.files.pop(a);return
  assert a=='/E/xwn586-kit/game' and b==c.KIT+'/game' and b not in self.dirs
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
 if f.mode=='corrupt-runner' and n.endswith('/run593.exe'):f.files[n]+=b'bad'
s=importlib.util.spec_from_file_location('recovery_stage_test',K/'stage_recovery003.py');recovery=importlib.util.module_from_spec(s);s.loader.exec_module(recovery);recovery.c=c;recovery.m=c.m
with tempfile.TemporaryDirectory(prefix='xwn594-recovery-model-') as tmp:
 for mode in ['pass','uncertain','changed-old-asset','extra-old-file','old-game-still-present','prior-save-changed','corrupt-runner','changed-stage','extra-startup']:
  c.K=Path(tmp)/mode;c.K.mkdir();recovery.K=c.K;c.P=c.K/'private';f=FTP(mode);files={}
  f.dirs={'/E/xwn586-kit',c.KIT,c.KIT+'/game',c.KIT+'/game/Data',c.KIT+'/game/Saved Games'}
  f.files[c.KIT+'/owner.json']=b'partialowner'
  for name,b in [('game/RCT.EXE',b'pristinegame'),('game/Data/Game.cfg',b'pristinecfg'),('game/Saved Games/XWN586.SV4',b'prior-save'),('run593.exe',b'runner')]:
   p=c.K/'payload'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);files[name]=dict(path=str(p),bytes=len(b),sha256=sha(b))
   if name.startswith('game/'):f.files[c.KIT+'/'+name]=b
  expected={n[5:]:r for n,r in files.items() if n.startswith('game/')}
  q=dict(files=files,reuse_expected=expected,runtime_module_pins={'kernel32.dll':sha(b'module')})
  old=dict(completed=False,temporary_hook_installed=False,before={n:dict(bytes=len(f.files[n]),sha256=sha(f.files[n])) for n in c.FILES},staged={c.KIT+'/owner.json':dict(bytes=12,sha256=sha(b'partialowner'))})
  (c.K/'stage001.json').write_text(json.dumps(old));(c.K/'supervisor001-stage.json').write_text(json.dumps(dict(closed=True,completed=False)))
  (c.K/'package003.json').write_text('{}')
  c.verify=lambda:q;c.boot_work_closed=lambda:None;c.budget=lambda:None
  c.m.connect=lambda **kw:f;c.m.baseline=lambda *a:None;c.m.names=names;c.m.get=get;c.m.put=put;c.m.keep=keep
  def cold(n,r,o):f.calls.append(('cold',n));return get(f,n,True)
  c.m.cold_pair=cold
  def startup(f,armed):
   rows=names(f,c.m.START);assert set(rows)<={'xwnsetup.cmd','desktop.ini'}|({'xwn594.cmd'} if armed else set())
   if armed:assert get(f,c.HOOK)==c.hook()
   return rows
  c.startup=startup
  if mode=='changed-old-asset':f.files[c.KIT+'/game/RCT.EXE']+=b'changed'
  if mode=='extra-old-file':f.files[c.KIT+'/game/unknown']=b'unknown'
  if mode=='old-game-still-present':f.dirs.add('/E/xwn586-kit/game')
  if mode=='prior-save-changed':f.files[c.KIT+'/game/Saved Games/XWN586.SV4']+=b'changed'
  try:recovery.run();staged=True
  except AssertionError:staged=False
  assert staged==(mode in ['pass','uncertain','changed-stage','extra-startup']),mode
  assert not any(x[0] in ['mkdir','rename'] for x in f.calls),mode
  if not staged:
   assert c.HOOK not in f.files and not any(x[0]=='launch' for x in f.calls);cases.append(dict(case=mode,refused_without_hook=True));continue
  assert get(f,c.KIT+'/game/Saved Games/XWN586.SV4')==b'prior-save'
  assert [x for x in f.calls if x[0]=='put']==[('put',c.KIT+'/run593.exe'),('put',c.HOOK)]
  count=len(f.calls)
  try:recovery.run()
  except AssertionError:pass
  else:raise AssertionError('Repeated recovery admitted')
  assert len(f.calls)==count
  if mode=='changed-stage':f.files[c.KIT+'/game/RCT.EXE']+=b'changed'
  if mode=='extra-startup':f.files[c.m.START+'/unknown.cmd']=b'unknown'
  try:c.launch();launched=True
  except AssertionError:launched=False
  assert launched==(mode in ['pass','uncertain']),mode
  if not launched:cases.append(dict(case=mode,launch_refused=True));continue
  assert sum(x[0]=='launch' for x in f.calls)==1
  try:c.launch()
  except AssertionError:pass
  else:raise AssertionError('Repeated launch admitted')
  assert sum(x[0]=='launch' for x in f.calls)==1
  assert bool(read(c.K/'launch001.json').get('reply_uncertain'))==(mode=='uncertain')
  f.dirs.add(c.RESULT);f.files[c.RESULT+'/runner.txt']=b'modeled receipt';f.calls=[]
  c.collect();assert read(c.K/'collection001.json')['hook_removed'] and f.calls[0]==('rename',c.HOOK,c.USED)
  cases.append(dict(case=mode,no_move_replay=True,prior_save_preserved=True,hook_last=True,one_launch=True,hook_first=True))
out=K/'recovery-host002.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,cases=cases,pins={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['controller003.py','stage_recovery003.py','recovery_host002.py']},scope='Actual controller paths under transport fault models; not FTP or game proof'),indent=2)+'\n');print('Passed',len(cases),'recovery controller cases')
