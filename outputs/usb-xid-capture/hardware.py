"""New successor ticket; E-only native capture, no Windows launch or baseline writes."""
import argparse,datetime,ftplib,hashlib,importlib.util,io,json,os,socket,time
from pathlib import Path
K=Path(__file__).resolve().parent;REPO=K.parents[1]
QUEUE=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-hardware220/state')
CLAIM=QUEUE/'usb-xid-claimed.json';CLOSED=QUEUE/'usb-xid-closed.json'
RECORD=K/'physical001.json';ART=K/'artifacts/physical001'
REMOTE='/E/Applications/XWNXid226a'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
spec=importlib.util.spec_from_file_location('usb220',K.parent/'usb-hardware220/physical.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def save(r):
    tmp=RECORD.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n')
    for i in range(100):
        try:tmp.replace(RECORD);return
        except PermissionError:
            if i==99:raise
            time.sleep(.05)

def pins():
    old.pins()
    f=read(K/'freeze.json')
    for path,digest in f['files'].items():assert sha(Path(path).read_bytes())==digest,'Frozen input changed: '+path
    assert read(K/'emulator-review.json')['passed']
    assert read(K/'build004-review.json')['passed'] and not read(K/'build004-review.json')['emulator']
    return f

def ticket():
    assert CLAIM.exists() and not CLOSED.exists(),'No active successor ticket'
    assert read(CLAIM)['owner']=='usb-xid'
    for name in ['audio','usb','pci']:assert read(QUEUE/(name+'-closed.json'))['baseline_restored']
    for path in QUEUE.glob('*-claimed.json'):
        if path!=CLAIM:assert path.with_name(path.name.replace('-claimed','-closed')).exists(),'Other physical owner'

def claim():
    pins()
    assert not CLAIM.exists() and not CLOSED.exists(),'Never reuse a successor ticket'
    for name in ['audio','usb','pci']:assert read(QUEUE/(name+'-closed.json'))['baseline_restored']
    for path in QUEUE.glob('*-claimed.json'):assert path.with_name(path.name.replace('-claimed','-closed')).exists()
    with CLAIM.open('x') as out:json.dump(dict(owner='usb-xid',scope=__doc__,claimed_utc=utc(),report=str(K/'REPORT.md')),out,indent=2)
    ticket();print('Claimed new USB XID successor ticket; original queue records preserved')

def connect():
    ticket();f=old.FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=5);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        assert 'unleash' in f.getwelcome().lower()
        expected=read(old.CANON/'outputs/native-windows-physical-f/physical-cache-preflight.json')['ownership_marker']
        assert json.loads(old.get(f,'/F/xwn-deploy-v1.json'))==expected
        return f
    except BaseException:f.close();raise

def keep(name,data):
    path=ART/name;path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==data,'Changed evidence: '+name
    else:path.write_bytes(data)
    return dict(file=str(path.relative_to(K)).replace('\\','/'),bytes=len(data),sha256=sha(data))

def before_files():
    files={path:digest for path,digest in old.expected().items()}
    for path in old.auxiliary().values():files.setdefault(path,None)
    for path in read(old.RECORD)['companions'].values():files.setdefault(path,None)
    return files

def capture():
    pins();ticket();assert not RECORD.exists()
    r=dict(created_utc=utc(),physical_access=True,launch_requested=False,baseline_writes=False,windows_launch_requested=False,before={},after={},baseline_restored=False)
    save(r)
    with connect() as f:
        assert REMOTE.rsplit('/',1)[1].lower() not in old.names(f,'/E/Applications')
        r['config_before_names']=sorted(old.names(f,'/F/winnt/system32/config'))
        for i,(path,digest) in enumerate(before_files().items()):
            data=old.get(f,path);r['before'][path]=keep('before/%03d.bin'%i,data);save(r)
            if digest:assert sha(data)==digest,'Protected baseline drift: '+path
    r['captured_utc']=utc();save(r);print('Actual incoming baseline captured; no physical writes')

def launch():
    pins();r=read(RECORD);assert r.get('captured_utc') and not r['launch_requested'] and not r.get('staging_started')
    binary=(K/'artifacts/build004/bin/default.xbe').read_bytes();assert sha(binary)==read(K/'build004-review.json')['xbe_sha256']
    with connect() as f:
        for path,row in r['before'].items():assert sha(old.get(f,path))==row['sha256'],'Intervening baseline change'
        r['staging_started']=True;save(r);ticket();f.mkd(REMOTE)
        # The sole FTP write is the authored XBE in this unique E: directory.
        for at in range(0,len(binary),32768):
            ticket();f.storbinary(('STOR ' if at==0 else 'APPE ')+REMOTE+'/default.xbe',io.BytesIO(binary[at:at+32768]),1024)
        assert old.get(f,REMOTE+'/default.xbe')==binary
        r.update(launch_requested=True,launch_utc=utc(),command=r'SITE EXEC E:\Applications\XWNXid226a\default.xbe',binary_sha256=sha(binary));save(r)
        try:r['launch_reply']=f.sendcmd(r['command'])
        except (OSError,EOFError,ftplib.Error) as e:r['launch_uncertain']=type(e).__name__
        save(r)
    print('One native launch recorded; never repeat from a timeout')

def observe():
    r=read(RECORD);assert r['launch_requested'] and not r.get('collected_utc');until=time.monotonic()+45
    while time.monotonic()<until:
        sample=dict(utc=utc(),dashboard=False)
        try:
            with connect() as f:
                sample['dashboard']=True;log=old.get(f,REMOTE+'/xid.log',optional=True)
                sample['log_present']=log is not None
        except (OSError,EOFError,ftplib.Error) as e:sample['error_type']=type(e).__name__
        r.setdefault('observations',[]).append(sample);save(r)
        if sample.get('log_present'):r['dashboard_return_utc']=utc();save(r);print('Dashboard returned with capture log');return
        time.sleep(4)
    print('Observer bound reached; no repeat launch')

def collect():
    pins();r=read(RECORD);assert r.get('dashboard_return_utc') and not r.get('collected_utc')
    with connect() as f:
        r['log']=keep('xid.log',old.get(f,REMOTE+'/xid.log'));save(r)
        for i,(path,row) in enumerate(r['before'].items()):
            r['after'][path]=keep('after/%03d.bin'%i,old.get(f,path));save(r)
        r['baseline_exact']=all(r['after'][path]['sha256']==row['sha256'] for path,row in r['before'].items())
        r['config_names_exact']=sorted(old.names(f,'/F/winnt/system32/config'))==r['config_before_names']
        r['binary_exact']=sha(old.get(f,REMOTE+'/default.xbe'))==r['binary_sha256']
    r.update(collected_utc=utc(),dashboard_verified=True);save(r)
    assert r['baseline_exact'] and r['config_names_exact'] and r['binary_exact'],'Hold ticket on unexpected drift'
    r['baseline_restored']=True;save(r);print('Capture preserved; every selected incoming byte remains exact')

def close():
    ticket();r=read(RECORD);assert r.get('collected_utc') and r.get('baseline_restored') and r.get('dashboard_verified')
    assert (K/'REPORT.md').is_file() and (K/'physical001-review.json').is_file()
    with CLOSED.open('x') as out:json.dump(dict(owner='usb-xid',closed_utc=utc(),baseline_restored=True,report=str(K/'REPORT.md'),declaration='Native capture returned to dashboard; all selected baseline files remained byte exact; Windows was not launched.'),out,indent=2)
    print('USB XID successor ticket closed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['claim','capture','launch','observe','collect','close']);a=p.parse_args()
    try:globals()[a.action]()
    except BaseException as e:
        if RECORD.exists():
            r=read(RECORD);r.setdefault('failures',[]).append(dict(action=a.action,utc=utc(),type=type(e).__name__));save(r)
        raise
