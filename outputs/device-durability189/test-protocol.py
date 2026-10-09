"""Offline unique189 failure/rollback/collection tests; no network or console access."""
import importlib.util,json,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('controller',k/'physical.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
original_ready=c.ready;probe=c.probe_path.read_bytes();seed={}
for name,row in c.previous['after'].items():
    if row:seed[name if name.startswith('/') else dict(c.aux).get(name,'unused-observer')]=(c.ws/row['path']).read_bytes()
assert c.sha(seed[c.startup])==c.expected_startup
assert c.sha(seed['/F/winnt/system32/config/system'])==c.expected_system
class Fake:
    def __init__(self,failure):self.data=dict(seed);self.puts=[];self.sent=[];self.failure=failure
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def mkd(self,path):self.data[path]=b''
    def sendcmd(self,cmd):
        assert json.loads(c.record.read_text())['launch_requested'];assert self.data[c.startup]==c.test_startup
        self.sent.append(cmd)
        if self.failure=='uncertain':raise OSError('Injected lost launch reply')
        return '200 offline mock ONLY'
def put(f,path,data):
    f.puts.append((path,data))
    if f.failure=='startup' and path==c.startup and data==c.test_startup:f.failure=None;raise OSError('Injected startup write failure')
    f.data[path]=data
c.m.get=lambda f,path,optional=False:f.data.get(path) if optional else f.data[path]
c.m.put=put;c.m.owner=lambda f:None
c.m.missing=lambda f,path:(_ for _ in ()).throw(AssertionError('Exists')) if path in f.data else None
tests=[]
for failure in ['startup','uncertain','collect','none']:
    with tempfile.TemporaryDirectory(prefix='xwn189-offline-') as tmp:
        c.k=Path(tmp);c.ws=c.k;c.art=c.k/'artifacts/physical';c.record=c.k/'physical.json'
        c.ready=lambda:None
        f=Fake(failure);c.m.connect=lambda:f
        try:c.launch(True)
        except OSError:
            assert failure=='startup' and not f.sent and f.data[c.startup]==seed[c.startup]
            r=json.loads(c.record.read_text());assert not r['startup_enabled'] and not r['launch_requested']
            tests.append('startup_failure_restores_before_any_launch')
            continue
        assert len(f.sent)==1
        if failure=='uncertain':assert json.loads(c.record.read_text())['reply_uncertain']=='OSError'
        try:c.launch(True)
        except AssertionError:pass
        else:raise AssertionError('Repeated launch accepted')
        assert len(f.sent)==1
        tests.append(failure+'_request_before_send_and_repeat_blocked')
        f.data[c.remote+'/observer.log']=b'offline mock log only';f.puts=[]
        if failure=='collect':f.data[c.fixed[0]['path']]+=b'injected drift'
        try:c.collect()
        except AssertionError:
            assert failure=='collect';r=json.loads(c.record.read_text());assert r['collection_failure'] and not r['startup_enabled']
            tests.append('partial_collection_closes_after_startup_restore')
        else:
            assert failure!='collect';r=json.loads(c.record.read_text());assert r['helper_exact'] and r['startup_backup_exact'] and r['collected_utc']
            tests.append(failure+'_startup_first_collection')
        assert f.puts==[(c.startup,seed[c.startup])]
        try:c.collect()
        except AssertionError:pass
        else:raise AssertionError('Repeated collection accepted')
        assert f.puts==[(c.startup,seed[c.startup])]
        tests.append(failure+'_collection_repeat_blocked')
dest=k/'protocol-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,tests=tests,offline_mock_only=True,physical_access=False,readiness_bypassed_only_in_isolated_mock=True,source_sha256=c.sha((k/'physical.py').read_bytes())),indent=2)+'\n',encoding='utf-8')
print('189 offline startup rollback, uncertain launch, partial collection and repeat guards passed')
