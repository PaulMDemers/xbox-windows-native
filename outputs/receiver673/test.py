"""Fresh fake-socket/child contract tests, no console or network access."""
import copy,datetime,hashlib,json,socket
from pathlib import Path
import readiness as d
K=Path(__file__).resolve().parent;P=Path('C:/xwn673/test001');out=K/'test001.json'
assert not P.exists() and not out.exists();P.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=json.loads(Path('C:/xwn672/config.json').read_text())
config=copy.deepcopy(original);config['fixture']='physical-candidate'
pins=[config[n] for n in ['attempt','build_id','candidate_sha256']]
r=dict(passed=False,physical_access=False,network_access=False,cases=[],source_pins={p.name:sha(p) for p in [K/'readiness.py',Path(__file__)]},original_config_sha256=sha(Path('C:/xwn672/config.json')))
class FakeSocket:
    calls=[];failbind=False
    def __init__(self,*args):self.calls.append('create')
    def __enter__(self):return self
    def __exit__(self,*args):self.calls.append('close')
    def setsockopt(self,*args):self.calls.append('exclusive')
    def bind(self,*args):
        self.calls.append('bind')
        if self.failbind:raise OSError('modeled bind failure')
    def settimeout(self,value):assert 0<value<=180
    def recvfrom(self,n):self.calls.append('receive');raise socket.timeout()
class Process:
    def __init__(self,pid,exitcode):self.pid=pid;self.exitcode=exitcode;self.polls=0
    def poll(self):self.polls+=1;return self.exitcode
def case(name,call,exc=None):
    try:call()
    except Exception as e:
        assert exc is not None and isinstance(e,exc),(name,type(e).__name__,exc)
    else:assert exc is None,name+' admitted invalid state'
    r['cases'].append(name)
def receive(cfg,tag,**kw):return d.receive(cfg,*pins,P/(tag+'.ready.json'),P/(tag+'-capture'),socket_factory=FakeSocket,**kw)
try:
 case('actual672 bad fixture rejected before readiness',lambda:receive(original,'bad-fixture'),ValueError)
 assert not FakeSocket.calls and not (P/'bad-fixture.ready.json').exists()
 for key,value in [('attempt','01'*16),('build_id','01'*32),('candidate_sha256','01'*32),('port',0),('port',True),('port',65536),('fixture','host-loopback')]:
    bad=dict(config);bad[key]=value
    case('reject '+key+' '+str(value)[:12],lambda:receive(bad,'invalid'),ValueError)
 assert not FakeSocket.calls
 case('invalid duration before bind',lambda:receive(config,'duration',seconds=181),ValueError)
 assert not FakeSocket.calls
 FakeSocket.failbind=True
 case('bind failure produces no readiness',lambda:receive(config,'bind'),OSError)
 assert not (P/'bind.ready.json').exists() and FakeSocket.calls[-1]=='close'
 FakeSocket.failbind=False;FakeSocket.calls=[]
 case('valid modeled receive validates then binds and closes',lambda:receive(config,'valid'))
 assert FakeSocket.calls==['create','exclusive','bind','receive','close']
 ready=P/'valid.ready.json';state=json.loads(ready.read_text());assert state['manifest_validated']
 proc=Process(state['pid'],None)
 case('live owned receiver admitted',lambda:d.admit_live_receiver(proc,ready,config))
 assert proc.polls==1
 proc.exitcode=1
 case('child died during staging rejects final boundary',lambda:d.admit_live_receiver(proc,ready,config),RuntimeError)
 assert proc.polls==2
 for key,value in [('bound',False),('manifest_validated',False),('pid',state['pid']+1),('port',state['port']+1),('attempt','01'*16),('build_id','01'*32),('candidate_sha256','01'*32)]:
    bad=dict(state);bad[key]=value;path=P/('bad-'+key+'.json');path.write_text(json.dumps(bad))
    case('readiness reject '+key,lambda:d.admit_live_receiver(Process(state['pid'],None),path,config),ValueError)
 before=list(FakeSocket.calls)
 case('used receiver paths denied without socket',lambda:receive(config,'valid'),FileExistsError)
 assert before==FakeSocket.calls
 assert sha(Path('C:/xwn672/config.json'))==r['original_config_sha256']
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS',len(r['cases']),'receiver contract checks; no network or console access')
