"""Offline failure tests for request-before-send and startup-FIRST collection; no connection."""
import importlib.util,json,tempfile
from pathlib import Path
k=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('controller',k/'physical.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
old=c.k;probe=(old/'artifacts/build003/observer.exe').read_bytes()
source=k.parent/'video-word-physical187/artifacts'
seed={v['path']:(source/v['path'].lstrip('/')).read_bytes() for v in c.capture['files']}
for name,row in json.loads((old/'build-review.json').read_text())['providers'].items():seed['/F/winnt/system32/'+name]=Path(row['path']).read_bytes()
class Fake:
    def __init__(self,fail=False):self.data=dict(seed);self.puts=[];self.sent=[];self.fail=fail
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def mkd(self,path):self.data[path]=b''
    def sendcmd(self,cmd):
        assert json.loads(c.record.read_text())['launch_requested'];assert self.data[c.startup]==c.test_startup
        self.sent.append(cmd);return '200 mock test ONLY'
def put(f,path,data):
    f.puts.append((path,data))
    if f.fail and path==c.startup and data==c.test_startup:f.fail=False;raise OSError('Injected startup write failure')
    f.data[path]=data
c.m.get=lambda f,path,optional=False:f.data.get(path) if optional else f.data[path]
c.m.put=put;c.m.owner=lambda f:None
c.m.missing=lambda f,path:(_ for _ in ()).throw(AssertionError('Exists')) if path in f.data else None
c.ready=lambda:None
tests=[]
for fail in [True,False]:
    with tempfile.TemporaryDirectory(prefix='xwn188-protocol-') as tmp:
        c.k=Path(tmp);c.ws=c.k;c.art=c.k/'artifacts/physical';c.record=c.k/'physical.json'
        (c.k/'artifacts/build003').mkdir(parents=True);(c.k/'artifacts/build003/observer.exe').write_bytes(probe)
        (c.k/'build-review.json').write_bytes((old/'build-review.json').read_bytes())
        f=Fake(fail);c.m.connect=lambda:f
        try:c.launch(True)
        except OSError:
            assert fail and not f.sent and f.data[c.startup]==seed[c.startup]
            r=json.loads(c.record.read_text());assert not r['startup_enabled'] and not r['launch_requested'];tests.append('staging_failure_restores_startup_no_launch')
        else:
            assert not fail and len(f.sent)==1
            try:c.launch(True)
            except AssertionError:pass
            else:raise AssertionError('Repeated launch accepted')
            assert len(f.sent)==1;tests.append('request_persisted_before_send_and_relaunch_blocked')
            f.data[c.remote+'/observer.log']=b'offline collection fixture only';f.puts=[];c.collect()
            assert f.puts==[(c.startup,seed[c.startup])]
            r=json.loads(c.record.read_text());assert not r['startup_enabled'] and r['helper_exact'] and r['startup_backup_exact']
            tests.append('collect_first_and_only_write_restores_startup')
            try:c.collect()
            except AssertionError:pass
            else:raise AssertionError('Repeated collection accepted')
            tests.append('completed_collection_cannot_repeat')
        assert all(path in [c.startup,c.remote+'/observer.exe',c.remote+'/normal-startup.cmd'] for path,_ in f.puts)
dest=k/'protocol-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,tests=tests,offline_mock_only=True,physical_access=False,limits='Readiness dependency gate bypassed only in this isolated mock; production checks remain unchanged. No network or real files changed.'),indent=2)+'\n')
print('Startup failure/rollback, request-before-send, no relaunch/recollect and startup-FIRST tests passed')
