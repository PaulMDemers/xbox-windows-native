"""One owned native read preflight; hold requires a watched manual reset."""
import datetime,ftplib,hashlib,io,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn689')
sys.path.insert(0,str(W/'outputs/demo-audio-level256'))
from common001 import ticket
REMOTE='/E/Applications/XWNXcal689'
COMMAND=r'SITE EXEC E:\Applications\XWNXcal689\default.xbe'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def connect():
    ticket();c=read(P/'connection.json');f=ftplib.FTP()
    try:f.connect(c['host'],timeout=15);f.login(c['user'],c['password']);return f
    except BaseException:f.close();raise
def names(f,path):
    assert path in ['/E','/E/Applications',REMOTE]
    f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
    rows=[];f.retrlines('LIST',rows.append);result={}
    for row in rows:
        v=row.split(None,8);assert len(v)==9
        if v[8] not in ['.','..']:result[v[8]]={'directory':v[0].startswith('d'),'bytes':int(v[4])}
    return result
def get(f,path):
    assert path in [REMOTE+'/owner.json',REMOTE+'/default.xbe']
    b=io.BytesIO()
    def take(v):assert b.tell()+len(v)<=1024*1024;b.write(v)
    f.retrbinary('RETR '+path,take,32768);return b.getvalue()
def verify():
    r=read(K/'build001.json');assert r['passed'] and read(K/'compiled001.json')['passed'] and read(K/'review001.json')['passed']
    for n,v in r['source_pins'].items():assert sha((K/n).read_bytes())==v
    for n,v in r['artifacts'].items():assert sha((P/'build001'/n).read_bytes())==v['sha256']
    return (P/'build001/default.xbe').read_bytes()
def stage():
    data=verify();out=K/'stage001.json';assert not out.exists()
    r={'completed':False,'utc':utc(),'writes':[],'hook':False,'Windows':False,'console_C_accessed':False,'controller_sha256':sha(Path(__file__).read_bytes())};save(out,r)
    try:
        with connect() as f:
            r['before_e']=names(f,'/E');r['before_apps']=names(f,'/E/Applications')
            assert not any(n.lower()=='xwnxcal689' for n in r['before_apps'])
            r['writes'].append(REMOTE);save(out,r);f.mkd(REMOTE)
            owner=json.dumps({'attempt':'689physical001','purpose':'native read preflight; success-only SMC LED; manual reset; no encoder or GPU setup','xbe_sha256':sha(data)},sort_keys=True).encode()
            r['staged']={}
            for name,body in [('owner.json',owner),('default.xbe',data)]:
                path=REMOTE+'/'+name;r['writes'].append(path);save(out,r)
                f.storbinary('STOR '+path,io.BytesIO(body),32768);assert get(f,path)==body
                r['staged'][path]={'bytes':len(body),'sha256':sha(body)};save(out,r)
            assert set(names(f,REMOTE))=={'owner.json','default.xbe'}
        r['completed']=True
    except BaseException as e:r['failure_type']=type(e).__name__;raise
    finally:save(out,r)
def launch():
    verify();s=read(K/'stage001.json');assert s['completed']
    assert read(K/'ready001.json')['watch_and_reset_ready']
    assert s['controller_sha256']==sha(Path(__file__).read_bytes())
    out=K/'launch001.json';assert not out.exists()
    f=connect()
    try:
        for name,v in s['staged'].items():assert sha(get(f,name))==v['sha256']
        r={'utc':utc(),'requested':True,'command':COMMAND,'automatic_retry':False,'hook':False,'expected':'hold; green/amber pattern write only after read success; LED alone cannot prove second indicator acknowledgement; other colors inconclusive'}
        with out.open('x') as stream:json.dump(r,stream,indent=2)
        f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(COMMAND)
        except Exception as e:r['reply_uncertain']=type(e).__name__
        save(out,r);print(json.dumps(r))
    finally:f.close()
def collect():
    assert read(K/'launch001.json')['requested'] and read(K/'reset001.json')['user_confirmed_dashboard']
    out=K/'collection001.json';assert not out.exists()
    r={'completed':False,'utc':utc(),'hook':'none installed','manual_reset':True,'Windows_shutdown_proved':False,'native_memory_snapshot_collected':False};save(out,r)
    try:
        with connect() as f:
            s=read(K/'stage001.json')
            for name,v in s['staged'].items():
                a=get(f,name);assert a==get(f,name) and sha(a)==v['sha256']
            assert names(f,'/E')==s['before_e']
            apps=names(f,'/E/Applications');apps.pop('XWNXcal689');assert apps==s['before_apps']
            assert set(names(f,REMOTE))=={'owner.json','default.xbe'}
        r.update(completed=True,unrelated_directory_entries_unchanged=True,staged_bytes_unchanged=True)
    except BaseException as e:r['failure_type']=type(e).__name__;raise
    finally:save(out,r)
if __name__=='__main__':{'stage':stage,'launch':launch,'collect':collect}[sys.argv[1]]()
