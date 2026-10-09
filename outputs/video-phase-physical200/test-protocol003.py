"""Host-only state-transition tests: prelaunch rollback, uncertain launch, startup-first collection/failure."""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'protocol-tests003.json';assert not dest.exists()
root=k/'artifacts/protocol-tests003';root.mkdir(exist_ok=False)
sys.argv=['physical-controller.py','inspect','control001']
spec=importlib.util.spec_from_file_location('controller_test',k/'physical-controller.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
original={v['path']:(k/'artifacts'/v['path'].lstrip('/')).read_bytes() for v in c.capture['files']}
class FakeFTP:
    def __init__(self):self.files=dict(original);self.dirs={'/F','/F/winnt/system32'};self.calls=[];self.fail_put=None;self.fail_get=None
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def cwd(self,path):self.cwd_path=path
    def retrlines(self,command,callback):
        assert command=='LIST'
        entries={p[len(self.cwd_path)+1:].split('/')[0] for p in set(self.files)|self.dirs if p.startswith(self.cwd_path+'/')}
        for name in sorted(entries):callback('-rw-r--r-- 1 owner group 1 Jan 1 00:00 '+name)
    def mkd(self,path):assert path not in self.dirs;self.dirs.add(path);self.calls.append(('mkdir',path))
    def delete(self,path):self.calls.append(('delete',path));del self.files[path]
    def sendcmd(self,command):self.calls.append(('launch',command));raise TimeoutError('injected uncertain reply')
def get(f,path,optional=False):
    f.calls.append(('get',path))
    if f.fail_get==path:f.fail_get=None;raise OSError('injected retrieval failure')
    if path not in f.files:
        if optional:return None
        raise FileNotFoundError(path)
    return f.files[path]
def put(f,path,data):
    f.calls.append(('put',path))
    if f.fail_put==path:f.fail_put=None;raise OSError('injected prelaunch staging failure')
    f.files[path]=data;assert get(f,path)==data
c.ready=lambda:None;c.m.owner=lambda f:None;c.m.get=get;c.m.put=put
checks=[]
def setup(label):
    p=root/label;p.mkdir();c.record=p/'physical.json';c.art=p/'physical';f=FakeFTP();c.m.connect=lambda:f;return f
def restored(f):
    assert all(f.files[p]==data for p,data in original.items() if p==c.system or p==c.startup or not p.endswith(c.mutable_suffixes))
    assert c.xwnown not in f.files
f=setup('prelaunch-failure');f.fail_put=c.changes[1][0]
try:c.deploy_launch(True);raise AssertionError('Failure not raised')
except OSError:pass
restored(f);r=c.read(c.record);assert not r['launch_requested'] and r['baseline_restored'] and not any(v[0]=='launch' for v in f.calls)
checks.append('Injected second-payload failure restores original startup/providers/SYSTEM and issues no launch')
f=setup('uncertain-launch');c.deploy_launch(True);r=c.read(c.record)
assert r['launch_requested'] and r['reply_uncertain']=='TimeoutError' and not r['baseline_restored']
launches=[v for v in f.calls if v[0]=='launch'];assert len(launches)==1
assert [v for v in f.calls if v[0]=='put'][-1]==('put',c.startup)
try:c.deploy_launch(True);raise AssertionError('Duplicate accepted')
except AssertionError as e:assert str(e)!='Duplicate accepted'
assert [v for v in f.calls if v[0]=='launch']==launches
f.files['/F/'+c.namespace+'/attempt.log']=b'Host-only mock result, not physical evidence'
for i in range(5):f.files['/F/'+c.namespace+'/sample%d/gdi-baseline.txt'%i]=b'Host-only mock sample'
f.files['/F/'+c.namespace+'/setup-before.log']=b'host-only checkpoint'
f.files['/F/'+c.namespace+'/setup-after.log']=b'host-only checkpoint'
at=len(f.calls);c.collect();restored(f)
assert f.calls[at+0]==('put',c.startup)
assert c.read(c.record)['collected_utc'] and c.read(c.record)['baseline_restored']
for name in ['setup-before.log','setup-after.log']:
 row=c.read(c.record)['after'][name];assert row and (ws/row['path']).read_bytes()==b'host-only checkpoint'
checks.append('Uncertain reply records exactly one launch; duplicate refused; collection first writes original startup then restores baseline')
f=setup('collection-failure');c.deploy_launch(True);f.fail_get='/F/winnt/system32/config/software';at=len(f.calls)
try:c.collect();raise AssertionError('Failure not raised')
except OSError:pass
restored(f);r=c.read(c.record);assert r['collection_failure'] and r['baseline_restored'] and not r.get('collected_utc')
assert f.calls[at]==('put',c.startup) and r['after']
try:c.collect();raise AssertionError('Recollection accepted')
except AssertionError as e:assert str(e)!='Recollection accepted'
checks.append('Partial collection failure preserves recorded evidence, restores baseline in finally and refuses recollection')
f=setup('unknown-delete');c.deploy_launch(True);r=c.read(c.record);f.files[c.xwnown]=b'unknown'
try:c.restore(f,r);raise AssertionError('Unknown deletion accepted')
except AssertionError as e:assert str(e)!='Unknown deletion accepted'
assert f.files[c.xwnown]==b'unknown' and f.files[c.startup]==original[c.startup]
checks.append('Unknown introduced DLL is retained; startup restored before refusing its deletion')
result=dict(passed=True,scope=__doc__,physical_access=False,real_launches=0,checks=checks,
    source_pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['physical-controller.py','test-protocol003.py']})
dest.write_text(json.dumps(result,indent=2)+'\n');print('Host protocol transitions passed; no real console access or launch')
