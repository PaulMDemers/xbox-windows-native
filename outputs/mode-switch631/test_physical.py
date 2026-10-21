"""Test the actual request-once function with fake FTP. No console access."""
import importlib.util,json,tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('controller631',Path(__file__).with_name('physical.py'))
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)

class Sock:
    def __init__(self):self.timeout=None
    def settimeout(self,n):self.timeout=n
class Fake:
    def __init__(self,uncertain=False):self.sock=Sock();self.calls=0;self.uncertain=uncertain
    def sendcmd(self,command):
        self.calls+=1;assert command==p.COMMAND
        if self.uncertain:raise TimeoutError('synthetic reply loss')
        return '200 accepted'
cases=[]
with tempfile.TemporaryDirectory(prefix='xwn631-') as root:
    for uncertain in (False,True):
        out=Path(root)/str(uncertain);f=Fake(uncertain)
        p.request_once(f,out);r=json.loads(out.read_text())
        assert f.calls==1 and f.sock.timeout==20 and r['requested']
        assert ('reply_uncertain' in r)==uncertain
        try:p.request_once(f,out)
        except FileExistsError:pass
        else:raise AssertionError('Duplicate request accepted')
        assert f.calls==1;cases.append(dict(uncertain_reply=uncertain,requests=1,duplicate_refused=True))
    for rows in ({'default.xbe':{'directory':False}}, {'evil.bin':{'directory':False}}, {'hd631.txt':{'directory':False,'bytes':32769}}, {'hd631.txt':{'directory':True,'bytes':0}}):
        original=p.m.names;p.m.names=lambda f,path:rows
        try:
            if 'default.xbe' in rows:assert p.listing(None)==rows
            else:
                try:p.listing(None)
                except AssertionError:pass
                else:raise AssertionError('Unsafe directory listing accepted')
        finally:p.m.names=original
out=p.K/'physical-host001.json';assert not out.exists()
out.write_text(json.dumps(dict(passed=True,console_access=False,scope='mocked request/listing only; no physical admission',cases=cases,listing_controls=4,controller_sha256=p.m.sha((p.K/'physical.py').read_bytes())),indent=2)+'\n')
print('Request timeout, duplicate refusal and owned listing checks passed; no console access')
