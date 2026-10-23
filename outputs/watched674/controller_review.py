"""Exercise actual674 launch boundary with fake FTP and owned child states."""
import copy,hashlib,importlib.util,json,socket
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn674/controller001');out=K/'controller-review001.json'
assert not P.exists() and not out.exists();P.mkdir()
spec=importlib.util.spec_from_file_location('physical674',K/'physical.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,controller_sha256=sha(K/'physical.py'),source_sha256=sha(Path(__file__)),cases=[])
cfg=dict(fixture='physical-candidate',expected_peer='192.0.2.1',port=50657,attempt='01'*16,build_id='02'*32,candidate_sha256='03'*32)
ready=P/'ready.json'
class Process:
 pid=673000;exitcode=None
 def poll(self):return self.exitcode
class FTP:
 def __init__(self,uncertain=False):self.sock=self;self.calls=0;self.uncertain=uncertain
 def settimeout(self,value):assert value==20
 def sendcmd(self,command):
  assert command==r'SITE EXEC E:\Applications\XWNLatch674\default.xbe';self.calls+=1
  if self.uncertain:raise socket.timeout('modeled uncertain reply')
  return '200 launch accepted'
try:
 state=dict(pid=Process.pid,bound=True,manifest_validated=True,**{n:cfg[n] for n in ['attempt','build_id','candidate_sha256','port']})
 ready.write_text(json.dumps(state))
 for uncertain in [False,True]:
  f=FTP(uncertain);process=Process();path=P/('uncertain.json' if uncertain else 'accepted.json')
  d.admit_and_request(f,path,process,ready,cfg)
  rec=json.loads(path.read_text());assert rec['requested'] and not rec['automatic_retry']
  assert ('reply_uncertain' in rec)==uncertain
  try:d.admit_and_request(f,path,process,ready,cfg)
  except FileExistsError:pass
  else:raise AssertionError('duplicate launch admitted')
  assert f.calls==1;r['cases'].append(dict(name='uncertain' if uncertain else 'accepted',site_calls=1,duplicate_refused=True))
 # Exercise the full launch function, including child death while protected
 # and staged file readbacks run. All external access is replaced with fakes.
 d.verify_binary=lambda:None;d.check=lambda f:None
 d.receiver_config=lambda:(cfg,{})
 d.m.sha=lambda b:sha(K/'physical.py') if b==Path(d.__file__).read_bytes() else 'same'
 rows={'/E/owned-control':dict(sha256='same')}
 def read(path):
  name=Path(path).name
  return {'stage001.json':dict(completed=True,staged=rows),'ready001.json':dict(available_to_reset=True),
   'firewall-verify001.json':dict(passed=True),'receiver-ready001.json':dict(bound=True),
   'preparation001.json':dict(completed=True,before=rows,source_pins={}),
   'controller-review001.json':dict(passed=True,controller_sha256=sha(K/'physical.py'))}[name]
 d.read=read
 f=FTP();process=Process();reads=[]
 class Connection:
  def __enter__(self):return f
  def __exit__(self,*a):pass
 d.m.connect=lambda **kw:Connection()
 def get(f,path):reads.append(path);process.exitcode=1;return b'owned test bytes'
 d.m.get=get
 real_admit=d.receiver.admit_live_receiver
 def use_test_ready(proc,path,c):return real_admit(proc,ready,c)
 d.receiver.admit_live_receiver=use_test_ready
 try:d.launch(process)
 except RuntimeError as e:assert str(e)=='receiver exited before launch'
 else:raise AssertionError('dead receiver admitted')
 assert len(reads)==2 and not f.calls and not (K/'launch001.json').exists()
 r['cases'].append(dict(name='actual launch: child dies during staging',readbacks=2,site_calls=0,launch_record_absent=True))
 # New manifest preflight rejects the exact kind of672 configuration error.
 bad=dict(cfg,fixture='signal672physical001')
 try:d.receiver.preflight(bad,cfg['attempt'],cfg['build_id'],cfg['candidate_sha256'])
 except ValueError:pass
 else:raise AssertionError('invalid fixture admitted')
 r['cases'].append(dict(name='bad fixture before receiver',site_calls=0))
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'controller cases; no physical connection')
