"""Serialized USB220 physical descriptor trial; existing stack, no driver installation."""
import argparse,datetime,ftplib,hashlib,io,json,os,shutil,socket,time,zipfile
from pathlib import Path

K=Path(__file__).resolve().parent
REPO=K.parents[1]
CANON=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
QUEUE=CANON/'outputs/device-hardware220'
PREV=K.parent/'usb-identification207'
RECORD=K/'physical001.json'
ART=K/'artifacts/physical001'
REMOTE='/F/xwnusb220a'
STARTUP='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
TEST=b'@echo off\r\nC:\\xwnusb220a\\usbprobe.exe\r\necho %errorlevel%>C:\\xwnusb220a\\exit.txt\r\nexit\r\n'
HIVES=['system','software','default','sam','security']
USB=['openhci.sys','usbd.sys','usbhub.sys','hidusb.sys','hidclass.sys','hidparse.sys','kbdhid.sys','mouhid.sys']
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(r):
    t=RECORD.with_suffix('.tmp');t.write_text(json.dumps(r,indent=2)+'\n')
    for i in range(100):
        try:t.replace(RECORD);return
        except PermissionError:
            if i==99:raise
            time.sleep(.05)

def keep(name,data):
    p=ART/name;p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data,'Evidence changed: '+name
    else:p.write_bytes(data)
    return dict(file=p.relative_to(K).as_posix(),bytes=len(data),sha256=sha(data))

def local(row):
    b=(K/row['file']).read_bytes();assert sha(b)==row['sha256'];return b

def ticket():
    assert read(QUEUE/'state/audio-closed.json')['baseline_restored'] is True
    assert read(QUEUE/'state/usb-claimed.json')['owner']=='usb'
    assert not (QUEUE/'state/usb-closed.json').exists(),'Ticket already closed'

class FTP(ftplib.FTP):
    def ntransfercmd(self,*a,**kw):
        s,n=super().ntransfercmd(*a,**kw);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n

def get(f,path,optional=False):
    b=io.BytesIO()
    def receive(data):
        assert b.tell()+len(data)<=200*1024**2;b.write(data)
    try:f.retrbinary('RETR '+path,receive,65536)
    except ftplib.error_perm as e:
        if optional and str(e).startswith('550'):return None
        raise
    return b.getvalue()

def connect(timeout=15):
    ticket();f=FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=timeout)
        f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        expected=read(CANON/'outputs/native-windows-physical-f/physical-cache-preflight.json')['ownership_marker']
        assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==expected,'Console ownership mismatch'
        assert 'unleash' in f.getwelcome().lower(),'Dashboard identity not established'
        return f
    except BaseException:f.close();raise

def put(f,path,data):
    ticket()
    for at in range(0,max(1,len(data)),32768):
        f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
    assert get(f,path)==data,'Readback failed: '+path

def names(f,path):
    f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
    rows=[];f.retrlines('LIST',rows.append);parts=[v.split(None,8) for v in rows]
    assert all(len(v)==9 for v in parts),'LIST parse failure'
    return {v[8].lower() for v in parts}

def pins():
    p=read(K/'prepared.json')
    for path,digest in p['pins'].items():assert sha(Path(path).read_bytes())==digest,'Input drift: '+path
    assert read(PREV/'build-review.json')['passed']
    assert read(PREV/'emu003/audit.json')['descriptor_scope_observed']
    return p

def expected():
    rows=read(CANON/'outputs/video-upload-runtime211/capture.json')['files']
    mutable=('/config/system','/config/software','/config/default','/config/sam','/config/security',
             '/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')
    fixed={v['path']:v['sha256'] for v in rows if not v['path'].endswith(mutable)}
    providers=read(PREV/'owned-provider-review.json')['files']
    fixed.update({'/F/winnt/system32/drivers/'+n:providers[n]['sha256'] for n in USB})
    for path,digest in read(K/'audio-incoming-drivers.json')['files'].items():
        assert path not in fixed or fixed[path]==digest,'Conflicting incoming driver baseline'
        fixed[path]=digest
    return fixed

def auxiliary():
    return {**{n:'/F/winnt/system32/config/'+n for n in HIVES+['sysevent.evt','appevent.evt']},
            'setupapi.log':'/F/winnt/setupapi.log','trace.bin':'/F/winnt/system32/xwn-video-trace.bin'}

def capture():
    pins();ticket()
    assert shutil.disk_usage('C:/').free>=20*1024**3,'Preserve 20 GiB C: guard'
    if RECORD.exists():
        r=read(RECORD);assert not r['capture_complete'] and not r['launch_requested']
    else:
        ART.mkdir(parents=True,exist_ok=False)
        r=dict(created_utc=utc(),scope=__doc__,physical_access=False,capture_complete=False,
               launch_requested=False,startup_enabled=False,baseline_restored=False,before={},after={},
               keyboard_persistently_unplugged=True,normal_restart_method='manual, not yet observed',
               input_reports_available=False,driver_installed=False)
        save(r)
    with connect() as f:
        r['physical_access']=True;r['dashboard_before']=True;save(r)
        assert REMOTE.rsplit('/',1)[1].lower() not in names(f,'/F'),'Existing trial directory'
        for i,(path,digest) in enumerate(expected().items()):
            data=get(f,path);r['before'][path]=keep('before/fixed-%03d.bin'%i,data);save(r)
            assert sha(data)==digest,'Incoming fixed baseline drift: '+path
        for name,path in auxiliary().items():
            r['before'][name]=keep('before/'+name,get(f,path));save(r)
        assert get(f,STARTUP)==local(r['before'][STARTUP])
    rollback=ART/'incoming-rollback.zip'
    if not rollback.exists():
        with zipfile.ZipFile(rollback,'x',zipfile.ZIP_DEFLATED) as z:
            for p in sorted((ART/'before').iterdir()):z.write(p,'before/'+p.name)
    with zipfile.ZipFile(rollback) as z:
        assert all(z.read('before/'+p.name)==p.read_bytes() for p in (ART/'before').iterdir())
    r.update(capture_complete=True,captured_utc=utc(),rollback_sha256=sha(rollback.read_bytes()))
    save(r);print('Incoming baseline captured; no physical writes or launch',flush=True)

def launch():
    p=pins();r=read(RECORD);assert r['capture_complete'] and not r['launch_requested']
    assert read(K/'before-hive-audit.json')['passed'],'Incoming hives must be reviewed before launch'
    assert read(K/'before-allocation.json')['allocation_consistent'],'Incoming full F allocation must pass'
    assert not r.get('staging_started'),'Preserve partial staging; no automatic retry'
    with connect() as f:
        assert REMOTE.rsplit('/',1)[1].lower() not in names(f,'/F')
        for path in expected():assert get(f,path)==local(r['before'][path]),'Incoming baseline changed: '+path
        for n in HIVES:assert get(f,auxiliary()[n])==local(r['before'][n]),'Incoming hive changed: '+n
        r['staging_started']=True;save(r)
        f.mkd(REMOTE)
        put(f,REMOTE+'/usbprobe.exe',Path(p['binary']).read_bytes())
        put(f,REMOTE+'/normal-startup.cmd',local(r['before'][STARTUP]))
        put(f,REMOTE+'/incoming-rollback.zip',(ART/'incoming-rollback.zip').read_bytes())
        try:
            # Record intent first so interrupted writes cannot masquerade as untouched startup.
            r['startup_write_started']=True;save(r)
            put(f,STARTUP,TEST);r['startup_enabled']=True;save(r)
        except BaseException:
            put(f,STARTUP,local(r['before'][STARTUP]));r['startup_enabled']=False;save(r);raise
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe')
        save(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except ftplib.all_errors as e:r['launch_reply_uncertain']=type(e).__name__
        save(r)
    print('Single USB220 Windows launch recorded; never relaunch this trial',flush=True)

def observe():
    r=read(RECORD);assert r['launch_requested'] and not r.get('collected_utc')
    observations=r.setdefault('observations',[])
    until=time.monotonic()+45
    while time.monotonic()<until:
        try:
            with connect(timeout=5) as f:
                done='exit.txt' in names(f,REMOTE)
                observations.append(dict(utc=utc(),dashboard_ftp=True,collector_exit_file=done))
                if done:
                    r['dashboard_return_utc']=utc();save(r);print('Owned dashboard returned; collector exit file exists',flush=True);return
        except (OSError,EOFError,ftplib.Error) as e:
            observations.append(dict(utc=utc(),error_type=type(e).__name__))
        save(r);time.sleep(5)
    r['observation_bound_utc']=utc();save(r)
    print('Bound reached without confirmed dashboard return; no relaunch',flush=True)

def collect():
    pins();r=read(RECORD);assert r['launch_requested'] and not r.get('collected_utc')
    with connect() as f:
        # Recovery always restores the exact incoming startup before evidence work.
        put(f,STARTUP,local(r['before'][STARTUP]));r['startup_enabled']=False
        r['startup_restored_utc']=utc();r['dashboard_at_collection']=True;save(r)
        for n in ['usb.log','exit.txt']:
            data=get(f,REMOTE+'/'+n,optional=True)
            r['after'][n]=None if data is None else keep('after/'+n,data);save(r)
        for name,path in auxiliary().items():
            r['after'][name]=keep('after/'+name,get(f,path));save(r)
        for i,path in enumerate(expected()):
            r['after'][path]=keep('after/fixed-%03d.bin'%i,get(f,path));save(r)
        r['fixed_exact']=all(local(r['after'][p])==local(r['before'][p]) for p in expected())
        r['collector_exact']=sha(get(f,REMOTE+'/usbprobe.exe'))==read(PREV/'build-review.json')['binary_sha256']
        r['startup_backup_exact']=get(f,REMOTE+'/normal-startup.cmd')==local(r['before'][STARTUP])
        r['rollback_readback_exact']=sha(get(f,REMOTE+'/incoming-rollback.zip'))==r['rollback_sha256']
        r['collected_utc']=utc();save(r)
    print('Startup restored FIRST; raw results and post-run baseline captured',flush=True)

def restore():
    # Exact incoming SYSTEM restoration is deliberately AFTER preserving/validating after-hive evidence.
    r=read(RECORD);assert r.get('collected_utc') and not r['baseline_restored']
    assert read(K/'after-hive-audit.json')['passed'],'Preserve invalid hive state for recovery review'
    assert read(K/'after-allocation.json')['allocation_consistent'],'Preserve failed allocation state for recovery review'
    assert r['fixed_exact'] and r['collector_exact'] and r['rollback_readback_exact']
    with connect() as f:
        put(f,STARTUP,local(r['before'][STARTUP]))
        for name in HIVES:
            # Restore all incoming registry snapshots for the next device owner's exact baseline.
            before=local(r['before'][name]);after=local(r['after'][name])
            assert get(f,auxiliary()[name]) in [before,after],'Unexpected intervening hive change'
            if before!=after:put(f,auxiliary()[name],before)
            assert get(f,auxiliary()[name])==before
        for path in expected():assert get(f,path)==local(r['before'][path]),'Protected baseline drift'
        r['restored_hives']={n:sha(get(f,auxiliary()[n])) for n in HIVES}
        r['dashboard_verified_after_restore']=True
    r.update(baseline_restored=True,restored_utc=utc(),startup_enabled=False);save(r)
    print('Incoming startup, five hives and protected binaries readback verified at dashboard',flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('action',choices=['capture','launch','observe','collect','restore'])
    action=a.parse_args().action
    try:globals()[action]()
    except BaseException as e:
        if RECORD.exists():
            r=read(RECORD);r.setdefault('failures',[]).append(dict(action=action,utc=utc(),type=type(e).__name__));save(r)
        raise
