"""Bounded physical FTP helpers and immutable evidence for the audio220 ticket."""
import datetime,ftplib,hashlib,io,json,os,pathlib,socket,sys,time
sys.dont_write_bytecode=True
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
canonical=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
queue=canonical/'outputs/device-hardware220/state'
startup='/F/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
read=lambda p:json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
sha=lambda data:hashlib.sha256(data).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path,value):
    path=pathlib.Path(path);tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n')
    for attempt in range(100):
        try:tmp.replace(path);return
        except PermissionError:
            if attempt==99:raise
            time.sleep(.05)
def ticket():
    assert read(queue/'audio-claimed.json')['owner']=='audio'
    assert not (queue/'audio-closed.json').exists(),'Ticket already closed'
class FTP(ftplib.FTP):
    def ntransfercmd(self,*a,**kw):
        sock,n=super().ntransfercmd(*a,**kw);sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return sock,n
def connect(timeout=15):
    ticket();f=FTP()
    try:
        f.connect(os.environ['XWN_FTP_HOST'],timeout=timeout);f.login(os.environ['XWN_FTP_USER'],os.environ['XWN_FTP_PASSWORD'])
        assert json.loads(get(f,'/F/xwn-deploy-v1.json'))==read(repo/'outputs/native-windows-physical-f/physical-cache-preflight.json')['ownership_marker']
        return f
    except BaseException:f.close();raise
def get(f,path,optional=False):
    b=io.BytesIO()
    def receive(data):
        assert b.tell()+len(data)<=64*1024**2,'Unexpected large file';b.write(data)
    try:f.retrbinary('RETR '+path,receive,65536)
    except ftplib.error_perm as exc:
        if optional and str(exc).startswith('550'):return None
        raise
    return b.getvalue()
def put(f,path,data):
    for at in range(0,max(1,len(data)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
    assert get(f,path)==data,'Write readback mismatch: '+path
def names(f,path):
    f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.rstrip('/').lower()
    rows=[];f.retrlines('LIST',rows.append);entries=[v.split(None,8) for v in rows];assert all(len(v)==9 for v in entries)
    return {v[8]:dict(directory=v[0].startswith('d'),bytes=int(v[4])) for v in entries if v[8] not in ['.','..']}
def keep(folder,path,data):
    p=folder/path.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():assert p.read_bytes()==data,'Preserved evidence changed: '+str(p)
    else:p.write_bytes(data)
    return dict(bytes=len(data),sha256=sha(data))
def before():
    r=read(k/'capture002.json');assert r['passed'] and not r['physical_writes'];return r
def incoming(path):
    r=before();matches=[n for n in r['files'] if n.lower()==path.lower()];assert matches,path
    n=matches[0];data=(k/'artifacts/before002'/n.lstrip('/')).read_bytes();assert sha(data)==r['files'][n]['sha256'];return data
def fixed():
    mutable=('/config/system','/config/software','/config/default','/config/sam','/config/security','/config/sysevent.evt','/config/appevent.evt','/xwn-video-trace.bin','/setupapi.log')
    r=read(canonical/'outputs/video-upload-runtime211/capture.json')
    result={v['path']:v['sha256'] for v in r['files'] if not v['path'].endswith(mutable) and v['path']!=startup}
    providers=read(k/'providers001.json');assert providers['passed']
    for v in providers['files'].values():
        assert v['remote'] not in result or result[v['remote']]==v['sha256']
        result[v['remote']]=v['sha256']
    return result
def check_fixed(f):
    r={p:sha(get(f,p))==h for p,h in fixed().items()};assert all(r.values()),'Protected baseline mismatch';return r
def pins():
    ticket();r=read(k/'frozen001.json')
    for path,h in r.items():assert sha(pathlib.Path(path).read_bytes())==h,'Frozen input changed: '+path
def helpers():
    root=repo/'outputs/audio207/artifacts/hardware-package001/payload'
    for name,row in read(root/'MANIFEST.json')['files'].items():assert sha((root/name).read_bytes())==row['sha256'],name
    return root
