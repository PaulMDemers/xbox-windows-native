"""MIT. Exercise actual stage/launch/collection against bounded fake FTP faults."""
import importlib.util,json,tempfile,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('rct565test',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=c.read;keep=c.m.keep;sha=c.m.sha
prior=read(K.parent/'perspective558/stage001.json')['before'];base={n:Path(prior[n]['path']).read_bytes() for n in c.FILES}
cases=[]
class FTP:
 def __init__(self,mode):self.files=dict(base);self.files['/E/winnt/system32/kernel32.dll']=b'module';self.dirs=set();self.calls=[];self.sock=self;self.mode=mode
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def settimeout(self,n):assert n==20
 def sendcmd(self,command):
  assert command==c.pair.COMMAND and read(c.K/'launch001.json')['requested'];self.calls.append(('launch',command))
  if self.mode=='uncertain':raise TimeoutError()
  return '200 modeled'
 def mkd(self,n):assert n not in self.dirs;self.dirs.add(n);self.calls.append(('mkdir',n))
 def storbinary(self,command,stream,blocksize):
  assert command.startswith('STOR ') and blocksize==65536;n=command[5:];self.files[n]=stream.read();self.calls.append(('put',n))
  if self.mode=='corrupt' and n.endswith('/run565.exe'):self.files[n]+=b'corrupt'
 def rename(self,a,b):assert a==c.HOOK and b==c.USED and b not in self.files;self.calls.append(('rename',a,b));self.files[b]=self.files.pop(a)
def names(f,p):
 rows={}
 for n in set(f.files)|f.dirs:
  if n.startswith(p+'/'):
   tail=n[len(p)+1:];name=tail.split('/')[0];rows[name]=dict(directory='/' in tail or n in f.dirs,bytes=len(f.files.get(n,b'')))
 return rows
def get(f,n,optional=False):return f.files.get(n) if optional else f.files[n]
def put(f,n,b):f.files[n]=b;f.calls.append(('put',n))
with tempfile.TemporaryDirectory(prefix='xwn565-test-') as tmp:
 for mode in ['pass','uncertain','corrupt','existing-kit','changed-game','bad-hook','extra-startup','existing-result','changed-launcher','low-space','new-save']:
  c.K=Path(tmp)/mode;c.K.mkdir();c.P=c.K/'private';source=c.K/'payload';source.mkdir()
  files={}
  for name,b in [('run565.exe',b'runner-model'),('game/RCT.EXE',b'game-model'),('game/Data/Game.cfg',b'cfg-model')]:
   p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);files[name]=dict(path=str(p),bytes=len(b),sha256=sha(b))
  q=dict(files=files,directories=['game','game/Data','game/Saved Games'],runtime_module_pins={'kernel32.dll':sha(b'module')},total_bytes=30)
  (c.K/'package001.json').write_text('{}');(c.K/'console-space001.json').write_text(json.dumps(dict(free_bytes=0 if mode=='low-space' else 1024**3)))
  f=FTP(mode);c.verify=lambda:q;c.boot_work_closed=lambda:None;c.budget=lambda:None;c.m.connect=lambda **kw:f;c.m.baseline=lambda *a:None;c.m.names=names;c.m.get=get;c.m.put=put;c.m.cold_pair=lambda n,r,o:get(f,n,True);c.m.keep=keep
  if mode=='existing-kit':f.dirs.add(c.KIT)
  try:c.stage();staged=True
  except AssertionError:staged=False
  assert staged==(mode not in ['low-space','existing-kit','corrupt']),mode
  if not staged:
   assert not any(a[0]=='launch' for a in f.calls) and c.HOOK not in f.files;cases.append(dict(case=mode,refused_before_hook=True));continue
  st=read(c.K/'stage001.json');assert st['completed'] and st['temporary_hook_installed']
  calls=len(f.calls)
  try:c.stage()
  except AssertionError:pass
  else:raise AssertionError('duplicate stage')
  assert len(f.calls)==calls
  if mode=='changed-game':f.files[c.KIT+'/game/RCT.EXE']+=b'bad'
  if mode=='bad-hook':f.files[c.HOOK]+=b'bad'
  if mode=='extra-startup':f.files[c.m.START+'/bad.cmd']=b'bad'
  if mode=='existing-result':f.dirs.add(c.RESULT)
  if mode=='changed-launcher':f.files[c.m.TARGET]+=b'bad'
  try:c.launch();launched=True
  except AssertionError:launched=False
  assert launched==(mode in ['pass','uncertain','new-save']),mode
  if not launched:cases.append(dict(case=mode,launch_refused=True));continue
  assert sum(a[0]=='launch' for a in f.calls)==1
  try:c.launch()
  except AssertionError:pass
  else:raise AssertionError('duplicate launch')
  assert sum(a[0]=='launch' for a in f.calls)==1
  assert bool(read(c.K/'launch001.json').get('reply_uncertain'))==(mode=='uncertain')
  f.dirs.add(c.RESULT);f.files[c.RESULT+'/runner.txt']=b'pc model receipt'
  if mode=='new-save':f.files[c.KIT+'/game/Saved Games/Test.SV4']=b'new save'
  f.calls=[];c.collect();col=read(c.K/'collection001.json')
  assert col['completed'] and col['hook_removed'] and f.calls[0][0]=='rename'
  assert c.HOOK not in f.files and f.files[c.USED]==c.hook()
  if mode=='new-save':assert col['files'][c.KIT+'/game/Saved Games/Test.SV4']['sha256']==sha(b'new save')
  cases.append(dict(case=mode,one_launch=True,hook_first=True,collection=True))
out=K/'controller-host001.json';assert not out.exists();out.write_text(json.dumps(dict(passed=True,cases=cases,source_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest(),scope='Transport/evidence models only; no real console or game execution'),indent=2)+'\n');print('Passed',len(cases),'controller fault cases')
