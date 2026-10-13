"""Failure-oriented tests of actual transaction/package code with an in-memory FTP model."""
import copy,json,sys,tempfile,zipfile
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=Path(__file__).resolve().parent;sys.path.insert(0,str(W/'tools'))
from stock_e import *
receipt=K/'host001.json';assert not receipt.exists();checks=[]
def rejects(name,fn):
    try:fn()
    except (Refused,ValueError,KeyError,zipfile.BadZipFile):checks.append(name);return
    raise AssertionError('Accepted '+name)
data={ROOTS[0]+'/a.txt':b'owned',LAUNCHER:b'launcher'}
m=dict(version=1,profile='stock-e-1080i',files={p:info(b) for p,b in data.items()},directories=[],support={})
files,dirs=layout(m)
class P:
    files=files;dirs=dirs
    def read(self,p):return data[p]
class Remote:
    def __init__(self,occupied=(),bad=None):self.objects={p:None for p in occupied};self.writes=[];self.bad=bad
    def exists(self,p):return p.lower() in {k.lower() for k in self.objects}
    def mkdir(self,p):assert not self.exists(p);self.objects[p]=None
    def create(self,p,b):assert not self.exists(p);self.objects[p]=b;self.writes.append(p)
    def read(self,p):return b'corrupt' if p==self.bad else self.objects[p]
r=Remote();events=[];result=create(P(),r,lambda *x:events.append(x));assert result['overwritten_files']==0 and r.writes[-1]==LAUNCHER and r.objects[ROOTS[0]+'/a.txt']==b'owned';checks.append('complete launcher last')
for root in ROOTS:
    r=Remote([root.upper()]);rejects('occupied '+root,lambda:create(P(),r,lambda *x:None));assert not r.writes
r=Remote(bad=ROOTS[0]+'/a.txt');events=[];rejects('failed readback stops before launcher',lambda:create(P(),r,lambda *x:events.append(x)));assert LAUNCHER not in r.objects and events[-1][0]=='write_intent'
r=Remote();events=[]
def interrupt(kind,p,meta):
    events.append((kind,p,meta))
    if kind=='write_intent':raise Refused('simulated stop before transfer')
rejects('journal interruption leaves no launcher',lambda:create(P(),r,interrupt));assert not r.writes
for bad in ['/C/winnt/x','/F/winnt/x','/E/Apps/x','/E/winnt/../x','/E/winnt//x','/E/winnt/a\nb','/E/winnt/é','/E/winnt/a:b','/E/winnt/a\\b','/E/winnt/'+('x'*43)]:
    n=copy.deepcopy(m);n['files'][bad]=info(b'x');rejects('invalid path '+repr(bad),lambda:layout(n))
n=copy.deepcopy(m);n['files'][ROOTS[0]+'/A.TXT']=info(b'x');rejects('case alias',lambda:layout(n))
n=copy.deepcopy(m);n['directories']=[ROOTS[0]+'/a.txt'];rejects('file-directory alias',lambda:layout(n))
n=copy.deepcopy(m);n['files'][LAUNCHER]['sha256']='z'*64;rejects('nonhex hash',lambda:layout(n))
raw=b'XWN-CAPACITY-333\nSPACE 1 2884108288 5120024576 16384 5118754816 2944663552\nSPACE 6 8004132864 242055217152 65536 242025365504 100121837568\nCOMPLETE 333\n'
assert capacity(raw,768884736)[0]['free_bytes']==2944663552;checks.append('actual standard geometry')
for label,v in [('incomplete',raw[:-15]),('wrong partition',raw.replace(b'SPACE 1 ',b'SPACE 2 ')),('wrong start',raw.replace(b'2884108288',b'2884108289')),('wrong cluster',raw.replace(b'16384',b'65536')),('too little free',raw.replace(b'2944663552',b'100')),('invalid free',raw.replace(b'2944663552',b'99999999999'))]:rejects(label,lambda:capacity(v,768884736))
with tempfile.TemporaryDirectory(prefix='xwn343-host-') as t:
    t=Path(t);manifest=(json.dumps(m)+'\n').encode();policy=t/'policy.json';policy.write_text(json.dumps(dict(manifest_sha256=sha(manifest))))
    def archive(name,mutate=None,extra=False):
        dest=t/name
        with zipfile.ZipFile(dest,'x') as z:
            z.writestr('MANIFEST.json',manifest)
            for p,b in data.items():z.writestr('payload'+p,mutate if mutate is not None and p==LAUNCHER else b)
            if extra:z.writestr('extra',b'x')
        return dest
    p=Package(archive('ok.zip'),policy);assert p.files==m['files'];p.z.close();checks.append('complete archive verified')
    rejects('extra ZIP entry',lambda:Package(archive('extra.zip',extra=True),policy))
    rejects('corrupt payload',lambda:Package(archive('corrupt.zip',mutate=b'changed!'),policy))
    policy.write_text(json.dumps(dict(manifest_sha256='0'*64)));rejects('manifest pin mismatch',lambda:Package(t/'ok.zip',policy))
receipt.write_text(json.dumps(dict(passed=True,cases=len(checks),checks=checks,model='In-memory remote; no network, native or physical install validation',sources={p:sha((W/p).read_bytes()) for p in ['tools/stock_e.py','tools/install-stock-e.py']}),indent=2)+'\n')
print('PASS',len(checks),'transaction/package refusal cases')
