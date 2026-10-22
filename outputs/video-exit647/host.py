"""Accepted/uncertain one-shot control checks; no physical connection."""
import importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('control647',K/'physical.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
out=K/'host001.json';assert not out.exists()
class Fake:
    def __init__(self,fail):self.sock=self;self.fail=fail;self.calls=0
    def settimeout(self,n):assert n==20
    def sendcmd(self,c):
        assert c==r'SITE EXEC E:\Applications\XWNVideo647\default.xbe';self.calls+=1
        if self.fail:raise TimeoutError('injected')
        return '200 accepted'
with tempfile.TemporaryDirectory() as d:
    for fail in (False,True):
        f=Fake(fail);path=Path(d)/str(fail);p.request_once(f,path)
        assert ('reply_uncertain' in p.read(path))==fail
        try:p.request_once(f,path)
        except FileExistsError:pass
        else:raise AssertionError('duplicate launch')
        assert f.calls==1
r=dict(passed=True,physical_access=False,accepted_and_uncertain_one_shot=True,controller_sha256=p.m.sha((K/'physical.py').read_bytes()))
with out.open('x') as f:json.dump(r,f,indent=2);f.write('\n')
