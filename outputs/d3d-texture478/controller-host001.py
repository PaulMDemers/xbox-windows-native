"""Exercise actual launch/collection functions against explicit FTP/filesystem models."""
import importlib.util,json,sys,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;ROOT=Path('C:/xwn478/controller-host001');assert not ROOT.exists();ROOT.mkdir()
sys.path.insert(0,str(K));spec=importlib.util.spec_from_file_location('model478',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=json.loads((K.parent/'physical-busy472/stage001.json').read_text())
base={n:Path(old['before'][n]['path']).read_bytes() for n in [m.NORMAL,m.TARGET]}
originalK=m.K;cases=[]
for case in ['success','timeout','bad-hook','unknown-startup','existing-result','changed-launcher','existing-report','changed-candidate']:
 m.K=ROOT/case;m.K.mkdir();m.P=m.K/'private';m.P.mkdir();state=dict(base);state[m.HOOK]=m.hook();state[m.REMOTE+'/default.xbe']=m.BUILD.read_bytes();calls=[]
 stage=dict(completed=True,source_pins={},before={n:dict(sha256=m.sha(b)) for n,b in base.items()},staged={m.REMOTE+'/default.xbe':dict(sha256=m.sha(m.BUILD.read_bytes()))})
 (m.K/'physical001-stage.json').write_text(json.dumps(stage))
 def names(f,path):
  result={};prefix=path+'/'
  for n in state:
   if n.startswith(prefix):
    rest=n[len(prefix):];first=rest.split('/')[0];result[first]={'directory':'/' in rest}
  return result
 class F:
  sock=None
  def __enter__(self):self.sock=self;return self
  def __exit__(self,*args):return False
  def settimeout(self,n):assert n==20
  def sendcmd(self,s):calls.append(('SITE',s));assert s==r'SITE EXEC E:\Applications\XWNBoot478a\default.xbe';
  def rename(self,a,b):calls.append(('rename',a,b));assert a in state and b not in state;state[b]=state.pop(a)
 def send(s):
  calls.append(('SITE',s))
  if case=='timeout':raise TimeoutError('modeled reply uncertainty')
  return '200 EXEC command succeeded.'
 f=F();f.sendcmd=send;m.connect=lambda **kw:f;m.names=names;m.get=lambda f,n,optional=False:state.get(n) if optional else state[n]
 m.verify=lambda:m.BUILD.read_bytes();m.baseline=lambda f,mode:None
 if case=='bad-hook':state[m.HOOK]+=b'bad'
 if case=='unknown-startup':state[m.START+'/other.cmd']=b'x'
 if case=='existing-result':state[m.RESULT+'/runner.txt']=b'x'
 if case=='changed-launcher':state[m.TARGET]+=b'x'
 if case=='existing-report':state[m.REMOTE+'/report.bin']=b'x'
 if case=='changed-candidate':state[m.REMOTE+'/default.xbe']+=b'x'
 try:m.launch();ok=True
 except AssertionError:ok=False
 assert ok==(case in ['success','timeout'])
 assert len([v for v in calls if v[0]=='SITE'])==int(ok)
 if ok:
  r=json.loads((m.K/'physical001-launch.json').read_text());assert bool(r.get('reply_uncertain'))==(case=='timeout')
  try:m.launch()
  except AssertionError:pass
  else:raise AssertionError('accepted request repeated')
  assert len(calls)==1
  m.collect();r=json.loads((m.K/'physical001-collection.json').read_text());assert r['hook_removed'] and m.HOOK not in state and state[m.KITROOT+'/startup-used.cmd']==m.hook()
  assert all(state[n]==b for n,b in base.items())
  try:m.collect()
  except AssertionError:pass
  else:raise AssertionError('collection repeated')
 cases.append(dict(case=case,admitted=ok,site_requests=sum(x[0]=='SITE' for x in calls),calls=calls))
result=dict(passed=True,cases=cases,real_network=False,FTP_and_baseline_module_interfaces='MODELED',actual_launch_collect_functions=True,source_sha256=hashlib.sha256((originalK/'physical.py').read_bytes()).hexdigest())
(originalK/'controller-host001.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS 8 actual dispatcher cases; FTP/baseline modeled')
