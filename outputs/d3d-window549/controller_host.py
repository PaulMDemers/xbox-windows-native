"""MIT. Actual549 stage/request/cleanup with explicit FTP and evidence models."""
import hashlib,importlib.util,json,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'controller-host001.json';assert not out.exists()
s=importlib.util.spec_from_file_location('scene549',K/'controller.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
actual_read=c.read;actual_keep=c.m.keep;sha=c.m.sha
before=actual_read(K.parent/'boot-primer543/after1.json')['files']
base={n:Path(before[n]['path']).read_bytes() for n in c.FILES}
files={n:dict(path=str(Path('C:/xwn549/runner-build002')/n),bytes=(Path('C:/xwn549/runner-build002')/n).stat().st_size,sha256=sha((Path('C:/xwn549/runner-build002')/n).read_bytes())) for n in ['run549.exe','d3d.exe']}
q=dict(files=files,runtime_module_pins={'kernel32.dll':sha(b'modeled-module')})
cases=[]
class FTP:
    def __init__(self):self.files=dict(base);self.files['/E/winnt/system32/kernel32.dll']=b'modeled-module';self.dirs=set();self.calls=[];self.sock=self;self.mode='ok'
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def settimeout(self,n):assert n==20
    def sendcmd(self,command):
        assert command==r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
        assert actual_read(c.K/'launch001.json')['requested'];self.calls.append(('SITE',command))
        if self.mode=='uncertain':raise TimeoutError('modeled')
        return '200 modeled'
    def mkd(self,p):assert p not in self.dirs;self.dirs.add(p);self.calls.append(('mkdir',p))
    def rename(self,a,b):
        assert a==c.HOOK and b==c.USED and a in self.files and b not in self.files
        self.calls.append(('rename',a,b));self.files[b]=self.files.pop(a)

def names(f,p):
    rows={}
    for n in set(f.files)|f.dirs:
        if n.startswith(p+'/'):
            rest=n[len(p)+1:];name=rest.split('/')[0]
            rows[name]=dict(directory='/' in rest or n in f.dirs,bytes=len(f.files.get(n,b'')))
    return rows
def get(f,n,optional=False):
    if optional:return f.files.get(n)
    return f.files[n]
def put(f,n,b):
    f.calls.append(('put',n));f.files[n]=b
    if f.mode=='corrupt-write' and n.endswith('/run549.exe'):f.files[n]=b'corrupt'

with tempfile.TemporaryDirectory(prefix='xwn549-host-') as tmp:
    for mode in ['success','uncertain','changed-launcher','changed-module','bad-hook','unknown-startup','existing-result','changed-sample','extra-kit','result25','result24','result-directory','result-oversize','used-hook-exists','existing-kit','corrupt-write']:
        c.K=Path(tmp)/mode;c.K.mkdir();c.P=c.K/'private';(c.K/'package001.json').write_text('{}')
        f=FTP();c.verify=lambda:q;c.boot_work_closed=lambda:None;c.budget=lambda:None
        c.m.connect=lambda **kw:f;c.m.baseline=lambda *a:None;c.m.names=names;c.m.get=get;c.m.put=put
        c.m.cold_pair=lambda n,r,o:get(f,n,True);c.m.keep=actual_keep
        if mode=='existing-kit':f.dirs.add(c.KIT)
        if mode=='corrupt-write':f.mode=mode
        try:c.stage();staged=True
        except AssertionError:staged=False
        assert staged==(mode not in ['existing-kit','corrupt-write']),mode
        if not staged:
            assert not (c.K/'launch001.json').exists();assert not any(x[0]=='SITE' for x in f.calls)
            assert not actual_read(c.K/'stage001.json')['completed'];cases.append(dict(case=mode,stage_refused=True));continue
        st=actual_read(c.K/'stage001.json');assert st['temporary_hook_installed']
        assert len(f.calls)==5 and all(x[1].startswith(c.KIT) or x[1]==c.HOOK for x in f.calls)
        try:c.stage()
        except AssertionError:pass
        else:raise AssertionError('duplicate stage')
        assert len(f.calls)==5
        f.calls=[]
        if mode=='uncertain':f.mode=mode
        if mode=='changed-launcher':f.files[c.m.TARGET]+=b'x'
        if mode=='changed-module':f.files['/E/winnt/system32/kernel32.dll']=b'changed'
        if mode=='bad-hook':f.files[c.HOOK]+=b'x'
        if mode=='unknown-startup':f.files[c.m.START+'/other.cmd']=b'x'
        if mode=='existing-result':f.dirs.add(c.RESULT)
        if mode=='changed-sample':f.files[c.KIT+'/d3d.exe']+=b'x'
        if mode=='extra-kit':f.files[c.KIT+'/unexpected']=b'x'
        refuse=mode in ['changed-launcher','changed-module','bad-hook','unknown-startup','existing-result','changed-sample','extra-kit']
        try:c.launch();launched=True
        except AssertionError:launched=False
        assert launched!=refuse,mode
        assert len(f.calls)==int(launched)
        if not launched:cases.append(dict(case=mode,launch_refused=True));continue
        assert bool(actual_read(c.K/'launch001.json').get('reply_uncertain'))==(mode=='uncertain')
        try:c.launch()
        except AssertionError:pass
        else:raise AssertionError('duplicate launch')
        assert len(f.calls)==1
        f.calls=[]
        if mode in ['result24','result25']:
            for i in range(int(mode[6:])):f.files[c.RESULT+f'/r{i}.txt']=b'modeled'
        if mode=='result-directory':f.dirs.add(c.RESULT+'/subdir')
        if mode=='result-oversize':f.files[c.RESULT+'/large.bin']=bytes(2*1024**2+1)
        if mode=='used-hook-exists':f.files[c.USED]=b'other'
        try:c.collect();collected=True
        except AssertionError:collected=False
        assert collected==(mode not in ['result25','result-directory','result-oversize','used-hook-exists']),mode
        if mode=='used-hook-exists':assert not f.calls and c.HOOK in f.files
        else:
            assert f.calls==[('rename',c.HOOK,c.USED)] and c.HOOK not in f.files
            assert actual_read(c.K/'collection001.json')['hook_removed']
        if collected:
            r=actual_read(c.K/'collection001.json');assert r['completed'] and not r['graphics_pass'] and not r['normal_shutdown_proved']
        count=len(f.calls)
        try:c.collect()
        except AssertionError:pass
        else:raise AssertionError('duplicate collection')
        assert len(f.calls)==count
        cases.append(dict(case=mode,one_request=True,collected=collected,hook_removed=c.HOOK not in f.files))

r=dict(passed=True,cases=cases,case_count=len(cases),source_sha256=hashlib.sha256((K/'controller.py').read_bytes()).hexdigest(),physical_access=False,scope='Actual controller; modeled FTP/baseline/lease/space; real local file hashes, protected-byte guards and request journal. No guest or physical qualification.')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('PASS',len(cases),'controller cases')
