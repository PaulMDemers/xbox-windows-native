"""Fresh read-only physical snapshot while holding the persistent audio queue ticket."""
import datetime,ftplib,hashlib,io,json,os,pathlib,sys,time
sys.dont_write_bytecode=True
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
canonical=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
queue=canonical/'outputs/device-hardware220/state'
assert json.loads((queue/'audio-channel001-claimed.json').read_text())['owner']=='audio-channel001'
assert not (queue/'audio-channel001-closed.json').exists()
dest=k/'capture002.json';art=k/'artifacts/before002'
assert not dest.exists() and not art.exists(),'Preserve previous attempt'
art.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
r=dict(scope=__doc__,physical_access=True,physical_writes=False,launch_requested=False,created_utc=utc(),files={},inventories={},passed=False)
def save():
    tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n')
    for attempt in range(100):
        try:tmp.replace(dest);return
        except PermissionError:
            if attempt==99:raise
            time.sleep(0.05)
def get(f,path):
    b=io.BytesIO()
    def chunk(data):
        assert b.tell()+len(data)<=32*1024**2,'Unexpected large file';b.write(data)
    f.retrbinary('RETR '+path,chunk,65536);return b.getvalue()
def names(f,path):
    f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.rstrip('/').lower()
    rows=[];f.retrlines('LIST',rows.append)
    entries=[v.split(None,8) for v in rows];assert all(len(v)==9 for v in entries)
    return {v[8]:dict(directory=v[0].startswith('d'),bytes=int(v[4])) for v in entries if v[8] not in ['.','..']}
def capture(f,path,expected=None):
    if path in r['files']:return
    data=get(f,path);p=art/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    row=dict(bytes=len(data),sha256=sha(data),second_read_exact=False,expected=expected)
    r['files'][path]=row;save()
    assert get(f,path)==data,'Changed during cold capture: '+path
    row['second_read_exact']=True;save()
    if expected:assert row['sha256']==expected,'Protected incoming baseline differs: '+path
save()
try:
    with ftplib.FTP() as f:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=20)
        f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        marker=json.loads(get(f,'/F/xwn-deploy-v1.json'))
        assert marker==json.loads((repo/'outputs/native-windows-physical-f/physical-cache-preflight.json').read_text())['ownership_marker']
        r['dashboard_owner_verified']=True;save()
        latest=json.loads((canonical/'outputs/video-upload-runtime211/capture.json').read_text());assert latest['passed']
        mutable=('/config/system','/config/software','/config/default','/config/sam','/config/security','/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')
        for row in latest['files']:
            capture(f,row['path'],None if row['path'].endswith(mutable) else row['sha256'])
        for root in ['/F','/F/winnt/inf','/F/winnt/system32/config','/F/winnt/system32/drivers','/E/Applications/XWNFBoot','/E/Applications/XWNFBoot/loader']:
            r['inventories'][root]=names(f,root);save()
        for name,entry in r['inventories']['/F/winnt/system32/config'].items():
            if not entry['directory'] and name.lower().split('.')[0] in ['system','software','sam','security','default']:
                capture(f,'/F/winnt/system32/config/'+name)
        for name,entry in r['inventories']['/F/winnt/inf'].items():
            if not entry['directory']:capture(f,'/F/winnt/inf/'+name)
        for name,entry in r['inventories']['/F/winnt/system32/drivers'].items():
            if not entry['directory'] and (any(s in name.lower() for s in ['ac97','xwnaci','wdmaud','portcls','sysaudio','swmidi']) or name.lower()=='ks.sys'):
                capture(f,'/F/winnt/system32/drivers/'+name)
        for root in ['/E/Applications/XWNFBoot','/E/Applications/XWNFBoot/loader']:
            for name,entry in r['inventories'][root].items():
                if not entry['directory']:capture(f,root+'/'+name)
        target='/F/winnt/system32/drivers/xwnaci207.sys'
        r['target_driver_initially_present']=any(n.lower()=='xwnaci207.sys' for n in r['inventories']['/F/winnt/system32/drivers'])
        r.update(passed=True,completed_utc=utc());save()
        print('Cold capture complete: '+str(len(r['files']))+' files, no writes or launch',flush=True)
except BaseException as exc:
    r.update(error_type=type(exc).__name__,failed_utc=utc());save();raise
