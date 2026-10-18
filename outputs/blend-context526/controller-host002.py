"""Exercise actual launch/collection functions against explicit FTP/filesystem models."""
import ftplib,importlib.util,json,sys,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;ROOT=Path('C:/xwn526/controller-host002');assert not ROOT.exists();ROOT.mkdir(parents=True)
sys.path.insert(0,str(K));spec=importlib.util.spec_from_file_location('model526',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=json.loads((K.parent/'physical-busy472/stage001.json').read_text())
base={n:Path(old['before'][n]['path']).read_bytes() for n in [m.NORMAL,m.TARGET]}
originalK=m.K;cases=[]
# MODELED controller candidate uses qualified494 bytes before the new build.
m.BUILD=Path('C:/xwn494/build002/default.xbe')
for case in ['success','timeout','bad-hook','unknown-startup','existing-result','changed-launcher','existing-report','existing-witness','existing-refusal','changed-candidate','capacity22','capacity23','existing-context','context-full','context-partial','read-transient','read-permanent']:
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
  def sendcmd(self,s):calls.append(('SITE',s));assert s==r'SITE EXEC E:\Applications\XWNBoot526a\default.xbe';
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
 if case=='existing-witness':state[m.REMOTE+'/handoff.bin']=b'x'
 if case=='existing-refusal':state[m.REMOTE+'/refusal.bin']=b'x'
 if case=='existing-context':state[m.REMOTE+'/context.bin']=b'x'
 if case=='changed-candidate':state[m.REMOTE+'/default.xbe']+=b'x'
 try:m.launch();ok=True
 except AssertionError:ok=False
 assert ok==(case in ['success','timeout','capacity22','capacity23','context-full','context-partial','read-transient','read-permanent'])
 assert len([v for v in calls if v[0]=='SITE'])==int(ok)
 if ok:
  r=json.loads((m.K/'physical001-launch.json').read_text());assert bool(r.get('reply_uncertain'))==(case=='timeout')
  try:m.launch()
  except AssertionError:pass
  else:raise AssertionError('accepted request repeated')
  assert len(calls)==1
  if case.startswith('capacity'):
   for j in range(int(case[8:])):state[m.RESULT+f'/result{j}.txt']=b'modeled'
  if case=='capacity23':
   try:m.collect()
   except AssertionError:pass
   else:raise AssertionError('oversize result directory accepted')
   assert m.HOOK not in state
   assert not json.loads((m.K/'physical001-collection.json').read_text())['completed']
   cases.append(dict(case=case,admitted=ok,collection_refused=True,hook_removed=True,calls=calls));continue
  if case in ['context-full','context-partial']:
   host=Path('C:/xwn490/full002')
   state[m.REMOTE+'/report.bin']=(host/'case00.bin').read_bytes()
   state[m.REMOTE+'/handoff.bin']=(host/'witness000.bin').read_bytes()
   state[m.REMOTE+'/context.bin']=(host/'context000.bin').read_bytes()[:300 if case=='context-partial' else 400]
   (m.K/'build002.json').write_bytes((originalK.parent/'d3d-transform494/build002.json').read_bytes())
  failures=[0]
  def cold_get(f,n,optional=False):
   if case in ['read-transient','read-permanent'] and n==m.REMOTE+'/default.xbe' and any(v[0]=='rename' for v in calls):
    if case=='read-permanent' or failures[0]==0:
     failures[0]+=1;raise ftplib.error_perm('502 modeled PASV failure')
   return state.get(n) if optional else state[n]
  m.get=cold_get
  if case=='read-permanent':
   try:m.collect()
   except ftplib.error_perm:pass
   else:raise AssertionError('permanent read failure accepted')
   assert failures[0]==2 and m.HOOK not in state
   partial=json.loads((m.K/'physical001-collection.json').read_text());assert partial['hook_removed'] and not partial['completed'] and len(partial['read_failures'])==2
   cases.append(dict(case=case,read_attempts=2,hook_removed=True,completed=False));continue
  m.collect();r=json.loads((m.K/'physical001-collection.json').read_text());assert r['hook_removed'] and m.HOOK not in state and state[m.KITROOT+'/startup-used.cmd']==m.hook()
  if case=='context-full':assert r['context_decoded']['preceding_witness_close']==2 and not r['context_decoded']['own_close_attested']
  if case=='context-partial':assert 'context_decode_error' in r and 'context_decoded' not in r
  if case=='read-transient':assert failures[0]==1 and len(r['read_failures'])==1
  if case=='capacity22':assert len(r['result_directory'])==22 and all(m.RESULT+f'/result{j}.txt' in r['files'] for j in range(22))
  assert all(state[n]==b for n,b in base.items())
  try:m.collect()
  except AssertionError:pass
  else:raise AssertionError('collection repeated')
 cases.append(dict(case=case,admitted=ok,site_requests=sum(x[0]=='SITE' for x in calls),calls=calls))
result=dict(passed=True,cases=cases,real_network=False,FTP_and_baseline_module_interfaces='MODELED',actual_launch_collect_functions=True,source_sha256=hashlib.sha256((originalK/'physical.py').read_bytes()).hexdigest())
(originalK/'controller-host002.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS 17 actual dispatcher cases; FTP/baseline modeled')
