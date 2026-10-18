"""Actual controller with modeled FTP; never connects to console."""
import copy,hashlib,importlib.util,json,struct,tempfile
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller539',K/'controller.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
read=c.read;sha=c.m.sha
out=K/'host001.json';assert not out.exists()
q=dict(images={'1':read(K/'prepared001.json')['images']['1']});cases=[]
ready1=dict(ordinal=1,ready=True,watching_LED=True,manual_reset_available=True)
audit=dict(closed=True,hives_clean=True,ordinary_code_exact=True)
observer=dict(at_dashboard=True,user_report_received=True)
c.admit(1,ready1);cases.append('admit1')
for key in ready1:
    v=copy.deepcopy(ready1);v[key]=9 if key=='ordinal' else not v[key]
    try:c.admit(1,v)
    except AssertionError:cases.append('reject-'+key)
    else:raise AssertionError(key)
try:c.admit(2,ready1)
except AssertionError:cases.append('reject-second-launch')
else:raise AssertionError('second launch allowed')

class FTP:
    def __init__(self,files,mode):self.files=files;self.mode=mode;self.calls=[];self.sock=self
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def settimeout(self,t):assert t==20
    def sendcmd(self,command):
        self.calls.append(command)
        if self.mode=='timeout':raise TimeoutError()
        return '200 EXEC command succeeded.'
    def retrbinary(self,command,take,block):
        p=command.removeprefix('RETR ')
        if self.mode=='unreadable':raise OSError('modeled unreadable')
        take(self.files[p])

original_read=c.read
original_keep=c.m.keep
original_disk=c.shutil.disk_usage
with tempfile.TemporaryDirectory(prefix='xwn541-host-') as tmp:
    root=Path(tmp)
    for mode in ['success1','timeout','stale','changed','bad-owner','bad-xbe','bad-trace','duplicate']:
        case=root/mode;case.mkdir();c.K=case
        i=2 if mode=='success2' else 1
        row=q['images'][str(i)];remote=row['remote']
        trace=b'XWN-VID-TRACE01\n'+bytes(4080)
        files={n:(trace if n.endswith('xwn-video-trace.bin') else n.encode()) for n in c.FILES}
        if mode=='bad-trace':files[next(n for n in c.FILES if n.endswith('xwn-video-trace.bin'))]=bytes(4096)
        before=dict(completed=True,startup_listing={'xwnsetup.cmd':{}},files={n:dict(bytes=len(b),sha256=sha(b)) for n,b in files.items()})
        for n,r in [(f'before{i}.json',before),(f'ready{i}.json',ready2 if i==2 else ready1),('after1.json',before),('audit1.json',audit),('observer1.json',observer)]:
            (case/n).write_text(json.dumps(r))
        files[remote+'/default.xbe']=Path(row['path']).read_bytes()
        files[remote+'/owner.json']=c.owner(i,row)
        if mode=='changed':files[c.FILES[0]]=b'changed'
        if mode=='bad-owner':files[remote+'/owner.json']=b'wrong'
        if mode=='bad-xbe':files[remote+'/default.xbe']=b'wrong'
        f=FTP(files,mode)
        c.verify=lambda:q
        c.read=lambda p: before if p==case.parent/'stack-stop540/after1.json' else original_read(p)
        c.m.connect=lambda **kw:f
        c.m.baseline=lambda *args:None
        c.m.startup=lambda f:before['startup_listing']
        c.m.get=lambda f,n,*args:f.files[n]
        c.m.names=lambda f,n:dict.fromkeys(['owner.json','default.xbe']+(['report.bin'] if mode=='stale' else []),{})
        if mode=='duplicate':(case/f'launch{i}.json').write_text('{}')
        expected=mode in ('success1','timeout')
        try:c.launch(i)
        except AssertionError:
            assert not expected,mode
        else:assert expected,mode
        assert len(f.calls)==int(expected),(mode,f.calls)
        if expected:
            assert f.calls==[c.launch_command(i)]
            journal=original_read(case/f'launch{i}.json');assert journal['requested']
            if mode=='timeout':assert journal['reply_uncertain']=='TimeoutError'
            try:c.launch(i)
            except AssertionError:pass
            else:raise AssertionError('duplicate accepted')
            assert len(f.calls)==1
        cases.append('launch-'+mode)
    for mode,b,size,want in [('valid',b'abc',3,True),('short',b'ab',3,False),
                             ('oversize',b'x'*4097,4097,False),('unreadable',b'a',1,False)]:
        f=FTP({'/E/test/context.bin':b},mode)
        try:data=c.receipt(f,'/E/test','context.bin',{'context.bin':dict(bytes=size,directory=False)})
        except (AssertionError,ValueError,OSError):assert not want
        else:assert want and data==b
        cases.append('receipt-'+mode)
    assert c.receipt(FTP({},'absent'),'/E/test','context.bin',{}) is None
    cases.append('receipt-absent')
r=dict(passed=True,cases=cases,scope='Actual admission/launch/receipt code; FTP,baseline and file facts modeled; no staging or hardware qualification',
       source_sha256=sha((K/'controller.py').read_bytes()),physical_access=False,all_temp_files_removed=True)
out.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(cases),'controller cases')
