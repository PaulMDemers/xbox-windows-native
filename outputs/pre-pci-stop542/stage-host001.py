"""Model stage writes and cold captures using the actual controller."""
import importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller539stage',K/'controller.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
q=dict(images={'1':c.read(K/'prepared001.json')['images']['1']});out=K/'stage-host001.json';assert not out.exists()
cases=[]
class F:
    def __init__(self,mode):self.mode=mode;self.files={};self.dirs=set();self.writes=[]
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def mkd(self,p):
        assert p not in self.dirs;self.dirs.add(p);self.writes.append(p)
    def retrbinary(self,command,take,block):take(self.files[command[5:]])
def put(f,p,b):
    f.writes.append(p)
    if f.mode=='writefail':raise OSError('modeled write failure')
    f.files[p]=b
def get(f,p,*a):return b'corrupt' if f.mode=='corrupt' else f.files[p]
def names(f,p):
    if p=='/E/Applications':return {'XWNBoot542a':{}} if f.mode=='existing' else {}
    return {n.rsplit('/',1)[1]:dict(bytes=len(b),directory=False) for n,b in f.files.items() if n.rsplit('/',1)[0]==p}
c.verify=lambda:q;c.m.put=put;c.m.get=get;c.m.names=names
c.m.baseline=lambda *a:None;c.m.startup=lambda f:{'xwnsetup.cmd':{}}
with tempfile.TemporaryDirectory(prefix='xwn542-stage-host-') as tmp:
    root=Path(tmp)
    for mode in ['success','existing','writefail','corrupt']:
        c.K=root/mode;c.K.mkdir();f=F(mode);c.m.connect=lambda **kw:f
        try:c.stage()
        except (AssertionError,OSError):assert mode!='success'
        else:assert mode=='success'
        r=c.read(c.K/'stage001.json');assert r['completed']==(mode=='success')
        assert all(p.startswith('/E/Applications/XWNBoot542') for p in f.writes)
        assert len(f.writes)==(3 if mode=='success' else 0 if mode=='existing' else 2)
        count=len(f.writes)
        try:c.stage()
        except AssertionError:pass
        else:raise AssertionError('repeated stage')
        assert len(f.writes)==count
        cases.append('stage-'+mode)
    for phase in ['before1','after1']:
        c.K=root/phase;c.K.mkdir();c.P=c.K/'private';f=F('success');c.m.connect=lambda **kw:f
        row=q['images']['1'];remote=row['remote']
        f.files={remote+'/default.xbe':Path(row['path']).read_bytes(),remote+'/owner.json':c.owner(1,row)}
        facts={'stage001.json':{'completed':True},'launch1.json':{'requested':True},'observer1.json':{'at_dashboard':True,'user_report_received':True},
               'ready1.json':dict(ordinal=1,ready=True,watching_LED=True,manual_reset_available=True)}
        for n,r in facts.items():(c.K/n).write_text(json.dumps(r))
        c.m.cold_pair=lambda n,r,out:n.encode()
        c.snapshot(phase);r=c.read(c.K/(phase+'.json'))
        assert r['completed'] and len(r['files'])==10 and not r['remote_writes']
        if phase=='after1':assert r['receipts']==dict.fromkeys(c.RECEIPTS)
        try:c.snapshot(phase)
        except AssertionError:pass
        else:raise AssertionError('repeated capture')
        cases.append('snapshot-'+phase)
out.write_text(json.dumps(dict(passed=True,cases=cases,source_sha256=c.m.sha((K/'controller.py').read_bytes()),
    scope='actual stage/capture with modeled FTP,baseline and paired cold bytes; no real hardware',physical_access=False),indent=2)+'\n')
print('PASS',len(cases),'stage/capture cases')
