"""Kernel-context753 batched setup prefix before CR22 on user-identified1.6. E only, no hook."""
import datetime,ftplib,hashlib,io,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn753')
sys.path.insert(0,str(W/'outputs/demo-audio-level256'))
from common001 import ticket
REMOTE='/E/Applications/XWNMode753'
COMMAND=r'SITE EXEC E:\Applications\XWNMode753\default.xbe'
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def connect():
    ticket();c=read(P/'connection.json');f=ftplib.FTP()
    try:f.connect(c['host'],timeout=15);f.login(c['user'],c['password']);return f
    except BaseException:f.close();raise
def names(f,path):
    assert path.startswith('/E') and '..' not in path
    f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
    rows=[];f.retrlines('LIST',rows.append);result={}
    for row in rows:
        v=row.split(None,8);assert len(v)==9
        if v[8] not in ['.','..']:result[v[8]]={'directory':v[0].startswith('d'),'bytes':int(v[4])}
    return result
def get(f,path):
    assert path.startswith(REMOTE+'/') or path.startswith('/E/xwn-mode753-')
    b=io.BytesIO()
    def take(v):
        assert b.tell()+len(v)<=1024*1024;b.write(v)
    f.retrbinary('RETR '+path,take,32768);return b.getvalue()
def verify():
    r=read(K/'build001.json');assert r['passed'] and all(read(K/n)['passed'] for n in ['model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','review001.json'])
    for n,v in r['files'].items():assert sha((P/'build001'/n).read_bytes())==v['sha256']
    for n in ['main.c','layout.h','layout.c','probe.c','probe.h','Makefile']:assert sha((K/n).read_bytes())==r['files'][n]['sha256']
    for n,v in read(K/'sources001.json').items():assert sha((K/n).read_bytes())==v
    for n,v in read(K/'review001.json')['checks'].items():assert sha((K/n).read_bytes())==v
    return (P/'build001/bin/default.xbe').read_bytes()
def stage():
    data=verify();out=K/'stage001.json';assert not out.exists()
    r={'completed':False,'utc':utc(),'writes':[],'startup_hook':False,'windows_intended':False,'console_C_accessed':False,'controller_sha256':sha(Path(__file__).read_bytes())};save(out,r)
    try:
        with connect() as f:
            r['before_e']=names(f,'/E');r['before_apps']=names(f,'/E/Applications')
            assert not any(n.lower().startswith('xwn-mode753-') for n in r['before_e'])
            assert not any(n.lower()=='xwnmode753' for n in r['before_apps'])
            r['writes'].append(REMOTE);save(out,r);f.mkd(REMOTE)
            owner=json.dumps({'attempt':'753physical001','purpose':'kernel-context preserving prefix then seven horizontal timing writes then CR04, CR05, CR00, CR02 and CR03 bytes with own saved-value restoration before output enable; no vertical, encoder, clock, scanout or CR1b/CR22/CR33 writes; automatic dashboard return after15seconds; no native handoff or Windows','xbe_sha256':sha(data)},sort_keys=True).encode()
            r['staged']={}
            for name,body in [('owner.json',owner),('default.xbe',data)]:
                path=REMOTE+'/'+name;r['writes'].append(path);save(out,r)
                f.storbinary('STOR '+path,io.BytesIO(body),32768)
                assert get(f,path)==body
                r['staged'][path]={'bytes':len(body),'sha256':sha(body)};save(out,r)
            assert set(names(f,REMOTE))=={'owner.json','default.xbe'}
        r['completed']=True
    except BaseException as e:r['failure_type']=type(e).__name__;raise
    finally:save(out,r)
def launch():
    verify();s=read(K/'stage001.json');assert s['completed']
    assert read(K/'ready001.json')['continue_authorized'] and read(K/'ready001.json')['dashboard_confirmed']
    assert s['controller_sha256']==sha(Path(__file__).read_bytes())
    out=K/'launch001.json';assert not out.exists()
    f=connect()
    try:
        for name,v in s['staged'].items():assert sha(get(f,name))==v['sha256']
        assert not any(n.lower().startswith('xwn-mode753-') for n in names(f,'/E'))
        r={'utc':utc(),'requested':True,'command':COMMAND,'automatic_retry':False,'hook':False,'observation':'user authorized continued diagnostics; no repeat launch; kernel-context CR03 checkpoint after qualified horizontal prefix and CR04/CR05/CR00/CR02 with own saved-value recovery; no native handoff; automatic return intended after15seconds'}
        with out.open('x') as stream:json.dump(r,stream,indent=2)
        f.sock.settimeout(20)
        try:r['reply']=f.sendcmd(COMMAND)
        except Exception as e:r['reply_uncertain']=type(e).__name__
        save(out,r);print(json.dumps(r))
    finally:f.close()
def collect():
    assert read(K/'launch001.json')['requested'];assert read(K/'collection-ready001.json')['dashboard_confirmed'];out=K/'collection001.json';assert not out.exists()
    r={'completed':False,'utc':utc(),'hook':'none installed; no cleanup required','reports':{}};save(out,r)
    try:
        with connect() as f:
            rows=names(f,'/E');s=read(K/'stage001.json')
            for name,v in s['staged'].items():assert sha(get(f,name))==v['sha256']
            reports=[n for n in rows if n.lower().startswith('xwn-mode753-') and n.lower().endswith('.json')]
            assert 0<len(reports)<=14
            d=P/'collection001';d.mkdir()
            for n in sorted(reports):
                assert not rows[n]['directory'] and rows[n]['bytes']<=32768
                a=get(f,'/E/'+n);assert a==get(f,'/E/'+n) and len(a)==rows[n]['bytes']
                (d/n).write_bytes(a);r['reports'][n]={'sha256':sha(a),'bytes':len(a),'data':json.loads(a)}
            remaining={n:v for n,v in rows.items() if n not in reports}
            assert remaining==s['before_e'],'E-root entry change outside reports'
            apps=names(f,'/E/Applications');apps.pop('XWNMode753');assert apps==s['before_apps']
            r['unrelated_directory_entries_unchanged']=True
        r.update(completed=True,dashboard_returned=True,windows_shutdown_proved=False)
    except BaseException as e:r['failure_type']=type(e).__name__;raise
    finally:save(out,r)
    print(json.dumps({'phases':[v['data']['phase'] for v in r['reports'].values()],'dashboard_returned':True}))
if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in ['stage','launch','collect'];globals()[sys.argv[1]]()
