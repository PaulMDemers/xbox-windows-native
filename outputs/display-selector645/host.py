"""Validate exact package/controller and one-shot launch behavior without hardware."""
import importlib.util
import json
import tempfile
from pathlib import Path

K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('trial645',K/'physical.py')
p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
out=K/'host001.json';assert not out.exists()

class Fake:
    sock=None
    def __init__(self,fail):self.sock=self;self.fail=fail;self.requests=[];self.timeout=None
    def settimeout(self,value):self.timeout=value
    def sendcmd(self,command):
        self.requests.append(command)
        if self.fail:raise TimeoutError('uncertain injected reply')
        return '200 accepted'

with tempfile.TemporaryDirectory() as folder:
    for fail in (False,True):
        f=Fake(fail);path=Path(folder)/str(fail)
        p.request_once(f,path)
        assert f.requests==[p.COMMAND] and f.timeout==20
        data=p.read(path);assert data['requested'] and not data['test_hook']
        assert ('reply_uncertain' in data)==fail
        try:p.request_once(f,path)
        except FileExistsError:pass
        else:raise AssertionError('Duplicate request allowed')
        assert len(f.requests)==1
# Pure package checks; verify() includes the existing ownership ticket but no connection.
assert p.m.sha(p.verify())==p.POLICY['profiles']['480p']['sha256']
r=dict(passed=True,physical_access=False,accepted_and_uncertain_one_shot=True,
       controller_sha256=p.m.sha((K/'physical.py').read_bytes()),
       selector_host_tests='644/host001:16 passed',package='644/package002: exact staged bytes')
with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('Host/package checks passed; no console access')
