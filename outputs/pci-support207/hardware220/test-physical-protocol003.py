"""Exercise actual physical.py with an in-memory FTP endpoint; never opens a socket."""
import contextlib,ftplib,hashlib,importlib.util,io,json,os
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'artifacts/protocol003';assert not out.exists();out.mkdir(parents=True)
def save(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data))
class FakeFTP:
    def __init__(self,state):self.s=state;state['constructed']+=1;self.at='/'
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def close(self):pass
    def connect(self,*args,**kwargs):self.s['ops'].append(('connect',))
    def login(self,*args):pass
    def retrbinary(self,cmd,callback,blocksize):
        path=cmd[5:];self.s['ops'].append(('read',path))
        if path not in self.s['files']:raise ftplib.error_perm('550 absent')
        callback(self.s['files'][path])
    def storbinary(self,cmd,stream,blocksize):
        verb,path=cmd.split(' ',1);data=stream.read();self.s['ops'].append((verb,path))
        self.s['files'][path]=(self.s['files'].get(path,b'') if verb=='APPE' else b'')+data
        if path==self.s['startup'] and self.s.get('fail_startup'):
            self.s['fail_startup']=False;raise ftplib.error_temp('450 injected partial write')
    def cwd(self,path):self.at=path
    def pwd(self):return self.at
    def retrlines(self,cmd,callback):callback('drwxr-xr-x 1 user group 0 Jan 01 00:00 winnt')
    def mkd(self,path):self.s['ops'].append(('mkdir',path))
    def sendcmd(self,cmd):
        self.s['ops'].append(('launch',cmd))
        if self.s.get('uncertain'):raise TimeoutError('injected missing reply')
        return '200 accepted'
def setup(name,ticket=True):
    spec=importlib.util.spec_from_file_location('physical220_'+name,k/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    root=out/name;root.mkdir();m.repo=root;m.k=root/'outputs/pci-support207/hardware220';m.k.mkdir(parents=True)
    m.queue=root/'queue';m.queue.mkdir();m.record=m.k/'physical001.json';m.art=m.k/'artifacts/physical001'
    (root/'.git').mkdir();(root/'.git/HEAD').write_text('ref: refs/heads/codex/xbox-native-pci\n')
    for predecessor in ('audio','usb'):save(m.queue/(predecessor+'-closed.json'),dict(baseline_restored=True))
    if ticket:save(m.queue/'pci-claimed.json',dict(owner='pci'))
    marker=dict(purpose='in-memory test only');save(root/'outputs/native-windows-physical-f/physical-cache-preflight.json',dict(ownership_marker=marker))
    protected='/F/winnt/system32/drivers/baseline.sys';m.fixed=[dict(path=protected,sha256=m.sha(b'baseline-driver'))]
    m.aux=[('startup.cmd',m.startup),('system','/F/winnt/system32/config/system')]
    state=dict(constructed=0,ops=[],startup=m.startup,files={m.startup:b'normal startup\r\n','/F/winnt/system32/config/system':b'preserved-system',protected:b'baseline-driver','/F/xwn-deploy-v1.json':json.dumps(marker).encode()})
    m.FTP=lambda:FakeFTP(state)
    payload=m.k/'artifacts/build001';payload.mkdir(parents=True)
    review=dict(passed=True)
    for item in ('inventory',):
        data=(item+'-test-payload').encode();(payload/(item+'.exe')).write_bytes(data);review[item+'_sha256']=m.sha(data)
    save(m.k/'build001-review.json',review);save(m.k/'physical001-preflight.json',dict(ready_for_read_only_trial=True))
    save(m.k/'emulator004/audit.json',dict(diagnostic_usable=True));startup=m.k/'emulator004/artifacts/startup.cmd';startup.parent.mkdir();startup.write_bytes(b'test startup\r\n')
    save(m.k/'emulator004/fixture.json',dict(files={'F/'+m.startup[3:]:m.sha(startup.read_bytes())}))
    return m,state,protected
def writes(s):return [x for x in s['ops'] if x[0] in ('STOR','APPE','mkdir','launch')]
def refuses(fn):
    try:fn()
    except (AssertionError,FileNotFoundError,ftplib.error_temp):return
    raise AssertionError('Expected refusal')
results=[]
saved={key:os.environ.get(key) for key in ('XWN_FTP_HOST','XWN_FTP_USER','XWN_FTP_PASSWORD')}
try:
    for key in saved:os.environ[key]='in-memory-test'
    with contextlib.redirect_stdout(io.StringIO()):
        m,s,p=setup('no_ticket',False);refuses(m.connect);assert s['constructed']==0;results.append('No connection before ticket')
        m,s,p=setup('wrong_baseline');s['files'][p]=b'drift';refuses(m.capture);assert not writes(s);results.append('Baseline mismatch never writes')
        m,s,p=setup('success');m.capture();assert not writes(s);m.launch();assert sum(v[0]=='launch' for v in s['ops'])==1;refuses(m.launch)
        for name in ('inventory.log','observer.log','result.txt'):s['files'][m.remote+'/'+name]=b'evidence'
        before=len(s['ops']);m.collect();changed=[v for v in s['ops'][before:] if v[0] in ('STOR','APPE')]
        assert changed==[('STOR',m.startup)] and s['files'][m.startup]==b'normal startup\r\n'
        assert all(v['matched'] for v in m.read(m.record)['after_checks']);results.append('Single launch; restore startup first; preserve protected baseline')
        m,s,p=setup('startup_failure');m.capture();s['fail_startup']=True;refuses(m.launch)
        assert s['files'][m.startup]==b'normal startup\r\n' and not any(v[0]=='launch' for v in s['ops']);refuses(m.launch);results.append('Partial startup write rolls back; retry denied')
        m,s,p=setup('uncertain_launch');m.capture();s['uncertain']=True;m.launch();refuses(m.launch)
        assert sum(v[0]=='launch' for v in s['ops'])==1 and m.read(m.record)['launch_reply_uncertain']=='TimeoutError';results.append('Uncertain reply never permits relaunch')
        m,s,p=setup('post_capture_drift');m.capture();s['files'][p]=b'drift';refuses(m.launch);assert not writes(s);results.append('Post-capture driver drift refuses staging')
        m,s,p=setup('startup_drift');m.capture();s['files'][m.startup]=b'other startup';refuses(m.launch);assert not writes(s);results.append('Post-capture startup drift refuses staging')
        m,s,p=setup('closed_ticket');m.capture();save(m.queue/'pci-closed.json',dict(owner='pci'));count=s['constructed'];refuses(m.launch);assert s['constructed']==count;results.append('Closed ticket cannot reconnect')
finally:
    for key,value in saved.items():
        if value is None:os.environ.pop(key,None)
        else:os.environ[key]=value
dest=k/'protocol003-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(scope=__doc__,passed=True,cases=results,source_sha256=hashlib.sha256((k/'physical.py').read_bytes()).hexdigest()),indent=2)+'\n')
print('Passed '+str(len(results))+' actual harness protocol scenarios; no network')
