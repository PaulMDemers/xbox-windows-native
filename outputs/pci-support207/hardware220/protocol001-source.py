"""Serialized read-only PCI identification trial. Only unique helpers/startup writes."""
import argparse,datetime,ftplib,hashlib,io,json,os,socket
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[2]
queue=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-hardware220/state')
record=k/'physical001.json';art=k/'artifacts/physical001';remote='/F/xwnpci220a'
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
aux=[('startup.cmd',startup)]+[(name,'/F/winnt/system32/config/'+name) for name in ('system','software','default','sam','security','sysevent.evt','appevent.evt')]+[('setupapi.log','/F/winnt/setupapi.log'),('trace.bin','/F/winnt/system32/xwn-video-trace.bin')]
fixed=read(repo/'outputs/device-durability189/physical.json')['before_checks']
def save(r):
    tmp=record.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(record)
def guard():
    assert (repo/'.git/HEAD').read_text().strip()=='ref: refs/heads/codex/xbox-native-pci'
    assert not (queue/'pci-closed.json').exists(),'Closed ticket cannot access console'
    assert read(queue/'pci-claimed.json')['owner']=='pci','PCI ticket required'
    for name in ('audio','usb'):assert read(queue/(name+'-closed.json'))['baseline_restored'] is True
class FTP(ftplib.FTP):
    def ntransfercmd(self,*args,**kwargs):
        sock,n=super().ntransfercmd(*args,**kwargs);sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return sock,n
def get(f,path,optional=False):
    output=io.BytesIO()
    def receive(b):
        assert output.tell()+len(b)<=32*1024*1024,'Capture bound';output.write(b)
    try:f.retrbinary('RETR '+path,receive,65536)
    except ftplib.error_perm as exc:
        if optional and str(exc).startswith('550'):return None
        raise
    return output.getvalue()
def connect():
    guard();f=FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=20);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==read(repo/'outputs/native-windows-physical-f/physical-cache-preflight.json')['ownership_marker']
        return f
    except BaseException:f.close();raise
def put(f,path,data):
    assert path==startup or path.startswith(remote+'/'),'Write allowlist'
    for at in range(0,max(1,len(data)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
    assert get(f,path)==data,'Readback mismatch'
def preserve(name,data):
    p=art/name
    with p.open('xb') as file:file.write(data)
    return dict(path=p.relative_to(repo).as_posix(),sha256=sha(data),bytes=len(data))
def preserved(row):
    b=(repo/row['path']).read_bytes();assert sha(b)==row['sha256'];return b
def capture():
    guard();assert not record.exists();art.mkdir(parents=True,exist_ok=False)
    r=dict(scope=__doc__,created_utc=utc(),physical_access=True,physical_writes=False,launch_requested=False,startup_enabled=False,before={},after={},before_checks=[],baseline_restored=False)
    save(r)
    with connect() as f:
        # Capture actual incoming bytes, then require the protected known baseline.
        for name,path in aux:r['before'][name]=preserve('before-'+name,get(f,path));save(r)
        for index,row in enumerate(fixed):
            b=get(f,row['path']);r['before'][row['path']]=preserve('before-protected-'+str(index),b)
            r['before_checks'].append(dict(path=row['path'],actual=sha(b),expected=row['sha256'],matched=sha(b)==row['sha256']));save(r)
        assert all(v['matched'] for v in r['before_checks']),'Incoming baseline differs; no writes permitted'
        r['capture_complete_utc']=utc();save(r)
    print('PCI220 incoming baseline captured; no writes or launch')
def launch():
    guard();r=read(record);assert r.get('capture_complete_utc') and not r['launch_requested'] and not r['physical_writes']
    assert read(k/'emulator001/audit.json')['diagnostic_usable']
    assert read(k/'physical001-preflight.json')['ready_for_read_only_trial']
    review=read(k/'build001-review.json');assert review['passed']
    payload={name:(k/'artifacts/build001'/name).read_bytes() for name in ('inventory.exe','observer.exe')}
    for name,b in payload.items():assert sha(b)==review[name.split('.')[0]+'_sha256']
    test=(k/'emulator001/artifacts/startup.cmd').read_bytes();original=preserved(r['before']['startup.cmd'])
    assert sha(test)==read(k/'emulator001/fixture.json')['files']['F/'+startup[3:]]
    with connect() as f:
        # Reject changes since capture before touching the console.
        for name,path in aux:assert get(f,path)==preserved(r['before'][name]),'Incoming state changed since capture'
        for row in r['before_checks']:assert sha(get(f,row['path']))==row['actual']
        f.cwd('/F');assert f.pwd().replace('\\','/').rstrip('/').lower() in ('/f','f:')
        lines=[];f.retrlines('LIST',lines.append)
        entries=[line.split(None,8) for line in lines];assert all(len(v)==9 for v in entries)
        assert all(v[8].lower()!='xwnpci220a' for v in entries),'Unique remote path required'
        r['physical_writes']=True;r['staging_started_utc']=utc();save(r)
        try:
            f.mkd(remote)
            for name,b in payload.items():put(f,remote+'/'+name,b)
            put(f,remote+'/normal-startup.cmd',original)
            r['startup_enabled']=True;save(r);put(f,startup,test)
        except BaseException as exc:
            r['staging_error_type']=type(exc).__name__;save(r)
            put(f,startup,original);r['startup_enabled']=False;r['staging_startup_rollback']=True;save(r);raise
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe',keyboard_unplugged_authorization='Persistent human instruction in hardware220 handoff')
        save(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as exc:r['launch_reply_uncertain']=type(exc).__name__
        save(r)
    print('One authorized PCI220 observer launch requested; never repeat from timeout')
def collect():
    guard();r=read(record);assert r['launch_requested'] and not r.get('collected_utc')
    original=preserved(r['before']['startup.cmd']);test=(k/'emulator001/artifacts/startup.cmd').read_bytes()
    with connect() as f:
        # FIRST restore actual incoming startup, before any long collection.
        assert get(f,startup) in (original,test),'Unexpected startup drift'
        put(f,startup,original);r['startup_enabled']=False;r['startup_restored_utc']=utc();save(r)
        for name,path in [('inventory.log',remote+'/inventory.log'),('observer.log',remote+'/observer.log'),('result.txt',remote+'/result.txt'),*aux]:
            if name in r['after']:continue
            b=get(f,path,optional=name in ('inventory.log','observer.log','result.txt'))
            r['after'][name]=preserve('after-'+name,b) if b is not None else None;save(r)
        r['after_checks']=[]
        for index,row in enumerate(r['before_checks']):
            b=get(f,row['path']);key=row['path']
            if key not in r['after']:r['after'][key]=preserve('after-protected-'+str(index),b)
            else:assert b==preserved(r['after'][key]),'Changed since partial collection'
            r['after_checks'].append(dict(path=key,sha256=sha(b),matched=sha(b)==row['actual']));save(r)
        r['helpers_exact']=all(sha(get(f,remote+'/'+name))==sha((k/'artifacts/build001'/name).read_bytes()) for name in ('inventory.exe','observer.exe'))
        r['startup_backup_exact']=get(f,remote+'/normal-startup.cmd')==original
        r['dashboard_reply']=f.pwd();r['collected_utc']=utc();save(r)
    print('Incoming startup restored/read back first; physical evidence collected. Offline baseline audit required before queue close.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=('capture','launch','collect'));args=ap.parse_args()
    {'capture':capture,'launch':launch,'collect':collect}[args.action]()
