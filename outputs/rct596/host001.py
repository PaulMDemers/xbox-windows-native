"""Model actual assets-only move, hook-last staging, single launch and hook-first cleanup."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller596recoverytest',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
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
original_boot=c.boot_work_closed
with tempfile.TemporaryDirectory(prefix='xwn596-model-') as tmp:
 for mode in ['pass','uncertain','missing-cold-confirmation','changed-game','extra-game-file','old-save-changed','new-save-changed','changed-loader','changed-stage','extra-startup','existing-output','existing-used-hook']:
  c.K=Path(tmp)/mode;c.K.mkdir();stage.K=c.K;c.P=c.K/'private';f=FTP(mode);files={};preserved={}
  f.dirs={'/E/xwn593-kit',c.KIT,c.KIT+'/game'}
  for root,nameset in [('/E/xwn593-kit',['owner.json','run593.exe','startup-used594.cmd']),(c.KIT,['owner.json','run586.exe','startup-used591.cmd','startup-used592.cmd','startup-used594.cmd','load586.exe'])]:
   for name in nameset:
    n=root+'/'+name;b=n.encode();f.files[n]=b;p=c.K/('asset'+str(len(preserved)));p.write_bytes(b);preserved[n]=dict(path=str(p),bytes=len(b),sha256=sha(b))
  for name,b in [('game/RCT.EXE',b'game'),('game/Data/Game.cfg',b'cfg'),('game/Saved Games/XWN586.SV4',b'oldsave'),('game/Saved Games/XWN593.SV4',b'newsave')]:
   p=c.K/'payload'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);files[name]=dict(path=str(p),bytes=len(b),sha256=sha(b));f.files[c.KIT+'/'+name]=b
  files['load586.exe']=preserved[c.KIT+'/load586.exe']
  q=dict(files=files,reuse_expected={n[5:]:r for n,r in files.items() if n.startswith('game/')},preserved=preserved,runtime_module_pins={'kernel32.dll':sha(b'module')})
  (c.K/'hardware-ready001.json').write_text(json.dumps(dict(user_confirmed_off_10_seconds_and_dashboard=mode!='missing-cold-confirmation')))
  def reads(p):
   if str(p).replace(chr(92),'/').endswith('rct595/final001.json'):return dict(closed=True)
   if str(p).replace(chr(92),'/').endswith('rct586/final002.json'):return dict(passed=True)
   return read(p)
  c.read=reads;c.verify=lambda:q;c.boot_work_closed=original_boot;c.budget=lambda:None
  c.m.connect=lambda **kw:f;c.m.baseline=lambda *a:None;c.m.names=names;c.m.get=get;c.m.put=put;c.m.keep=keep
  c.m.cold_pair=lambda n,r,o:get(f,n,True)
  def startup(f,armed):
   rows=names(f,c.m.START);assert set(rows)<={'xwnsetup.cmd','desktop.ini'}|({'xwn596.cmd'} if armed else set())
   if armed:assert get(f,c.HOOK)==c.hook()
   return rows
  c.startup=startup
  if mode=='changed-game':f.files[c.KIT+'/game/RCT.EXE']+=b'bad'
  if mode=='extra-game-file':f.files[c.KIT+'/game/unknown']=b'bad'
  if mode=='old-save-changed':f.files[c.KIT+'/game/Saved Games/XWN586.SV4']+=b'bad'
  if mode=='new-save-changed':f.files[c.KIT+'/game/Saved Games/XWN593.SV4']+=b'bad'
  if mode=='changed-loader':f.files[c.KIT+'/load586.exe']+=b'bad'
  if mode=='existing-output':f.dirs.add(c.RESULT)
  if mode=='existing-used-hook':f.files[c.USED]=b'old'
  try:stage.run();staged=True
  except AssertionError:staged=False
  assert staged==(mode in ['pass','uncertain','changed-stage','extra-startup']),mode
  if not staged:
   assert c.HOOK not in f.files and not any(x[0]=='launch' for x in f.calls);cases.append(dict(case=mode,refused_without_hook=True));continue
  assert [x for x in f.calls if x[0]=='put']==[('put',c.HOOK)]
  count=len(f.calls)
  try:stage.run()
  except AssertionError:pass
  else:raise AssertionError('Repeated staging admitted')
  assert len(f.calls)==count
  if mode=='changed-stage':f.files[c.KIT+'/game/RCT.EXE']+=b'bad'
  if mode=='extra-startup':f.files[c.m.START+'/unknown.cmd']=b'bad'
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
  cases.append(dict(case=mode,no_game_writes=True,one_launch=True,hook_first=True))
out=K/'host001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,cases=cases,pins={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['controller001.py','stage001.py','host001.py','batch_read001.py']},scope='Actual controller with modeled transport; no hardware or game proof'),indent=2)+'\n');print('Passed',len(cases),'controller cases')
