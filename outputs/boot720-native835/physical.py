"""Fixed720p Windows boot835: create-only boot staging, one SITE, no startup hook."""
import datetime,ftplib,hashlib,io,json,socket,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn835')
sys.path.insert(0,str(W/'outputs/demo-audio-level256'));from common001 import ticket,queue
R='/E/Applications/XWN16Boot835';PREFIX='xwn-boot835-'
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text());utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
class FTP(ftplib.FTP):
 def ntransfercmd(self,*a,**kw):
  s,n=super().ntransfercmd(*a,**kw);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
def connect(timeout=15):
 ticket();assert not (queue/'boot720835-install-active.lock').exists()
 c=read(Path('C:/xwn820/connection.json'));assert c['host']=='192.168.50.66';f=FTP()
 try:f.connect(c['host'],timeout=timeout);f.login(c['user'],c['password']);return f
 except BaseException:f.close();raise
def names(f,path):
 assert path in ['/E','/E/Applications',R] or path.startswith(R+'/')
 f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
 rows=[];f.retrlines('LIST',rows.append);v=[s.split(None,8) for s in rows];assert all(len(s)==9 for s in v)
 return {s[8]:{'directory':s[0][0]=='d','bytes':int(s[4])} for s in v if s[8] not in ['.','..']}
def allowed(p):return p.startswith(R+'/') or p.startswith('/E/'+PREFIX) or p in critical()
def get(f,p):
 assert allowed(p);b=io.BytesIO()
 def take(v):
  assert b.tell()+len(v)<=8*1024**2;b.write(v)
 f.retrbinary('RETR '+p,take,65536);return b.getvalue()
def critical():
 pkg=read(K/'package001.json')['files']
 suffix=['/system32/drivers/xwnfatx.sys','/system32/drivers/xboxvnt5.sys','/system32/xwnown.dll','/system32/config/system','/system32/config/software','/system32/config/default','/system32/config/sam','/system32/config/security','/loader/halxboxnt5.dll','/loader/xboxbvid.dll','/startup/xwnsetup.cmd']
 found={p:v for p,v in pkg.items() if any(p.lower().endswith(s) for s in suffix)}
 assert len(found)==len(suffix);return found
def verify():
 assert read(K/'installation001.json')['state']=='payload_installed'
 assert read(K/'installation-review001.json')['passed']
 b=read(K/'build001.json');assert b['passed']
 for n,v in b['files'].items():assert sha((P/'build001'/n).read_bytes())==v['sha256']
 chain=read(K/'chain002.json');assert chain['passed']
 for n,v in chain['artifacts'].items():assert sha((P/'chain002'/n).read_bytes())==v['sha256']
 assert read(K/'qualify001.json')['passed'] and read(K/'host006.json')['passed']
 c=read(K/'cpu-run010.json');assert c['passed'] and c['closed']
 for n,h in read(K/'launch-source-pins001.json').items():assert sha((K/n).read_bytes())==h
 return {'freeldr.sys':(P/'chain002/freeldr.sys').read_bytes(),'rosload.exe':(P/'chain002/rosload.exe').read_bytes(),'default.xbe':(P/'build001/bin/default.xbe').read_bytes()}
def stage():
 blobs=verify();out=K/'stage001.json';assert not out.exists()
 r={'completed':False,'utc':utc(),'hook':False,'console_C_accessed':False,'writes':[],'controller_sha256':sha(Path(__file__).read_bytes())};save(out,r)
 try:
  with connect() as f:
   r['before_e']=names(f,'/E');r['before_apps']=names(f,'/E/Applications');r['before_boot']=names(f,R)
   assert not any(n.lower().startswith(PREFIX) for n in r['before_e'])
   assert not any(n.lower() in {'owner835.json',*blobs} for n in r['before_boot'])
   r['critical_payload']={}
   for p,v in critical().items():
    data=get(f,p);assert len(data)==v['bytes'] and sha(data)==v['sha256'];r['critical_payload'][p]={'bytes':len(data),'sha256':sha(data)}
   owner=json.dumps({'attempt':'835physical001','purpose':'Xbox1.6 fixed720p Windows boot, retained kernel mode; ordinary desktop startup','source_pins_sha256':sha((K/'launch-source-pins001.json').read_bytes()),'boot_files':{n:sha(b) for n,b in blobs.items()}},sort_keys=True).encode()
   r['staged']={}
   for name,data in [('owner835.json',owner),*blobs.items()]:
    path=R+'/'+name;r['writes'].append(path);save(out,r)
    for at in range(0,max(1,len(data)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
    assert get(f,path)==data;r['staged'][path]={'bytes':len(data),'sha256':sha(data)};save(out,r)
   after=names(f,R)
   for n in ['owner835.json',*blobs]:after.pop(n)
   assert after==r['before_boot'];r['completed']=True
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:save(out,r)
def launch():
 verify();s=read(K/'stage001.json');assert s['completed'] and s['controller_sha256']==sha(Path(__file__).read_bytes())
 out=K/'launch001.json';assert not out.exists()
 f=connect()
 try:
  for p,v in {**s['critical_payload'],**s['staged']}.items():assert sha(get(f,p))==v['sha256']
  assert not any(n.lower().startswith(PREFIX) for n in names(f,'/E'))
  r={'utc':utc(),'requested':True,'command':r'SITE EXEC E:\Applications\XWN16Boot835\default.xbe','automatic_retry':False,'hook':False,'windows_intended':True,'expected_return':'None: normal startup leaves Windows desktop running','authorization':'Direct user request for1.6 fixed720p Windows boot'}
  with out.open('x') as stream:json.dump(r,stream,indent=2)
  f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['reply_uncertain']=type(e).__name__
  save(out,r);print(json.dumps(r))
 finally:f.close()
def collect():
 assert read(K/'launch001.json')['requested'];assert read(K/'dashboard001.json')['authenticated']
 out=K/'collection001.json';assert not out.exists();r={'completed':False,'utc':utc(),'hook':'none installed','reports':{}};save(out,r)
 try:
  with connect() as f:
   rows=names(f,'/E');reports=[n for n in rows if n.lower().startswith(PREFIX) and n.endswith('.json')];assert 1<=len(reports)<=12
   for p,v in read(K/'stage001.json')['staged'].items():assert sha(get(f,p))==v['sha256']
   d=P/'collection001';d.mkdir()
   for n in sorted(reports):
    data=get(f,'/E/'+n);assert len(data)==rows[n]['bytes']<=32768;(d/n).write_bytes(data)
    r['reports'][n]={'bytes':len(data),'sha256':sha(data),'data':json.loads(data)}
   r['completed']=True;r['windows_boot_proved']=False
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:save(out,r)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['stage','launch','collect'];globals()[sys.argv[1]]()
