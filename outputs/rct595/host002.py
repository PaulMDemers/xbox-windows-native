"""Model actual assets-only move, hook-last staging, single launch and hook-first cleanup."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller595recoverytest',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
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
  assert a=='/E/xwn593-kit/game' and b==c.KIT+'/game' and b not in self.dirs
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
 if f.mode=='corrupt-runner' and n.endswith('/load586.exe'):f.files[n]+=b'bad'

s=importlib.util.spec_from_file_location('stage_test',K/'stage001.py');stage=importlib.util.module_from_spec(s);s.loader.exec_module(stage);stage.c=c;stage.m=c.m
with tempfile.TemporaryDirectory(prefix='xwn595-model-') as tmp:
 for mode in ['pass','restore','uncertain','changed-old-asset','extra-old-file','destination-game-exists','prior-save-changed','new-save-changed','corrupt-runner','rename-error','changed-stage','extra-startup']:
  c.K=Path(tmp)/mode;c.K.mkdir();stage.K=c.K;c.P=c.K/'private';f=FTP(mode);files={};preserved={}
  f.dirs={stage.SOURCE,stage.SOURCE+'/game',c.KIT}
  for root,nameset in [(stage.SOURCE,['owner.json','run593.exe','startup-used594.cmd']),(c.KIT,['owner.json','run586.exe','startup-used591.cmd','startup-used592.cmd'])]:
   for name in nameset:
    n=root+'/'+name;b=n.encode();f.files[n]=b;p=c.K/('asset'+str(len(preserved)));p.write_bytes(b);preserved[n]=dict(path=str(p),bytes=len(b),sha256=sha(b))
  for name,b in [('game/RCT.EXE',b'pristinegame'),('game/Data/Game.cfg',b'pristinecfg'),('game/Saved Games/XWN586.SV4',b'oldsave'),('game/Saved Games/XWN593.SV4',b'newsave'),('load586.exe',b'loader')]:
   p=c.K/'payload'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);files[name]=dict(path=str(p),bytes=len(b),sha256=sha(b))
   if name.startswith('game/'):f.files[stage.SOURCE+'/'+name]=b
  expected={n[5:]:r for n,r in files.items() if n.startswith('game/')}
  q=dict(files=files,reuse_expected=expected,restore_assets=[],preserved=preserved,runtime_module_pins={'kernel32.dll':sha(b'module')})
  if mode=='restore':
   f.files[stage.SOURCE+'/game/Data/Game.cfg']=b'changedcfg'
   q['reuse_expected']['Data/Game.cfg']=dict(bytes=10,sha256=sha(b'changedcfg'));q['restore_assets']=['Data/Game.cfg']
  c.verify=lambda:q;c.boot_work_closed=lambda:None;c.budget=lambda:None
  c.m.connect=lambda **kw:f;c.m.baseline=lambda *a:None;c.m.names=names;c.m.get=get;c.m.put=put;c.m.keep=keep
  c.m.cold_pair=lambda n,r,o:get(f,n,True)
  def startup(f,armed):
   rows=names(f,c.m.START);assert set(rows)<={'xwnsetup.cmd','desktop.ini'}|({'xwn595.cmd'} if armed else set())
   if armed:assert get(f,c.HOOK)==c.hook()
   return rows
  c.startup=startup
  if mode=='changed-old-asset':f.files[stage.SOURCE+'/game/RCT.EXE']+=b'bad'
  if mode=='extra-old-file':f.files[stage.SOURCE+'/game/unknown']=b'unknown'
  if mode=='destination-game-exists':f.dirs.add(c.KIT+'/game')
  if mode=='prior-save-changed':f.files[stage.SOURCE+'/game/Saved Games/XWN586.SV4']+=b'bad'
  if mode=='new-save-changed':f.files[stage.SOURCE+'/game/Saved Games/XWN593.SV4']+=b'bad'
  try:stage.run();staged=True
  except (AssertionError,TimeoutError):staged=False
  assert staged==(mode in ['pass','restore','uncertain','changed-stage','extra-startup']),mode
  if not staged:
   assert c.HOOK not in f.files and not any(x[0]=='launch' for x in f.calls);cases.append(dict(case=mode,refused_without_hook=True));continue
  assert get(f,c.KIT+'/game/Saved Games/XWN586.SV4')==b'oldsave'
  assert get(f,c.KIT+'/game/Saved Games/XWN593.SV4')==b'newsave'
  assert [x for x in f.calls if x[0]=='put']==([('put',c.KIT+'/game/Data/Game.cfg')] if mode=='restore' else [])+[('put',c.KIT+'/load586.exe'),('put',c.HOOK)]
  count=len(f.calls)
  try:stage.run()
  except AssertionError:pass
  else:raise AssertionError('Repeated staging admitted')
  assert len(f.calls)==count
  if mode=='changed-stage':f.files[c.KIT+'/game/RCT.EXE']+=b'bad'
  if mode=='extra-startup':f.files[c.m.START+'/unknown.cmd']=b'bad'
  try:c.launch();launched=True
  except AssertionError:launched=False
  assert launched==(mode in ['pass','restore','uncertain']),mode
  if not launched:cases.append(dict(case=mode,launch_refused=True));continue
  assert sum(x[0]=='launch' for x in f.calls)==1
  try:c.launch()
  except AssertionError:pass
  else:raise AssertionError('Repeated launch admitted')
  assert sum(x[0]=='launch' for x in f.calls)==1
  assert bool(read(c.K/'launch001.json').get('reply_uncertain'))==(mode=='uncertain')
  f.dirs.add(c.RESULT);f.files[c.RESULT+'/runner.txt']=b'modeled receipt';f.calls=[]
  c.collect();assert read(c.K/'collection001.json')['hook_removed'] and f.calls[0]==('rename',c.HOOK,c.USED)
  cases.append(dict(case=mode,both_saves_preserved=True,hook_last=True,one_launch=True,hook_first=True))
out=K/'host002.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,cases=cases,pins={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['controller001.py','stage001.py','host002.py','batch_read001.py']},scope='Actual controller with modeled transport; no hardware or game proof'),indent=2)+'\n');print('Passed',len(cases),'controller cases')
