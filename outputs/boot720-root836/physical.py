"""Fresh fixed720p boot836. Create-only staging, one bounded SITE, collect once."""
import datetime,ftplib,hashlib,io,json,socket,sys,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn836');R='/E/Applications/XWN16Boot836';PREFIX='xwn-boot836-'
sys.path.insert(0,str(W/'outputs/demo-audio-level256'));from common001 import ticket
sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:json.loads(p.read_text());utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
class FTP(ftplib.FTP):
 def ntransfercmd(self,*a,**kw):
  s,n=super().ntransfercmd(*a,**kw);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
def connect(timeout=15):
 ticket();c=read(Path('C:/xwn820/connection.json'));assert c['host']=='192.168.50.66';f=FTP()
 try:f.connect(c['host'],timeout=timeout);f.login(c['user'],c['password']);return f
 except BaseException:f.close();raise
def names(f,p):
 assert p in ['/E','/E/Applications',R,R+'/loader']
 f.cwd(p);assert f.pwd().replace('\\','/').rstrip('/').lower()==p.lower()
 rows=[];f.retrlines('LIST',rows.append);v=[s.split(None,8) for s in rows];assert all(len(s)==9 for s in v)
 return {s[8]:{'directory':s[0][0]=='d','bytes':int(s[4])} for s in v if s[8] not in ['.','..']}
def get(f,p):
 assert p.startswith(R+'/') or p.startswith('/E/'+PREFIX) or p in read(K/'baseline001.json')['critical']
 b=io.BytesIO()
 def take(v):assert b.tell()+len(v)<=8*1024**2;b.write(v)
 f.retrbinary('RETR '+p,take,65536);return b.getvalue()
def verify():
 for n,h in read(K/'launch-source-pins001.json').items():assert sha((K/n).read_bytes())==h
 for n in ['root001','qualify001','host006','cpu-build010','cpu-run010','build001','chain002']:assert read(K/(n+'.json'))['passed']
 assert read(K/'cpu-run010.json')['closed']
 for n,v in read(K/'chain002.json')['artifacts'].items():assert sha((P/'chain002'/n).read_bytes())==v['sha256']
 for n,v in read(K/'build001.json')['files'].items():assert sha((P/'build001'/n).read_bytes())==v['sha256']
 return {'freeldr.sys':(P/'chain002/freeldr.sys').read_bytes(),'rosload.exe':(P/'chain002/rosload.exe').read_bytes(),'default.xbe':(P/'build001/bin/default.xbe').read_bytes()}
def stage():
 blobs=verify();out=K/'stage001.json';assert not out.exists()
 base=read(K/'baseline001.json');archive=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip')
 assert sha(archive.read_bytes())==base['archive_sha256']
 with zipfile.ZipFile(archive) as z:
  for n,v in base['support'].items():
   b=z.read('payload'+v['archive_path']);assert len(b)==v['bytes'] and sha(b)==v['sha256'];blobs[n]=b
 r={'completed':False,'utc':utc(),'hook':False,'console_C_accessed':False,'writes':[],'staged':{},'critical':{},'controller_sha256':sha(Path(__file__).read_bytes())};save(out,r)
 try:
  with connect() as f:
   r['before_apps']=names(f,'/E/Applications');assert R.rsplit('/',1)[1].lower() not in {n.lower() for n in r['before_apps']}
   r['before_e']=names(f,'/E');assert not any(n.lower().startswith(PREFIX) for n in r['before_e'])
   for p,v in base['critical'].items():
    b=get(f,p);assert len(b)==v['bytes'] and sha(b)==v['sha256'];r['critical'][p]={'bytes':len(b),'sha256':sha(b)}
   r['created_directories']=[R];save(out,r);f.mkd(R)
   r['created_directories'].append(R+'/loader');save(out,r);f.mkd(R+'/loader')
   owner=json.dumps({'attempt':'836physical001','purpose':'fixed720p Windows boot with FATX root-chain traversal fix','source_pins_sha256':sha((K/'launch-source-pins001.json').read_bytes()),'files':{n:sha(b) for n,b in blobs.items()}},sort_keys=True).encode()
   for n,b in [('owner836.json',owner),*blobs.items()]:
    p=R+'/'+n;r['writes'].append(p);save(out,r)
    for at in range(0,max(1,len(b)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+p,io.BytesIO(b[at:at+32768]),1024)
    assert get(f,p)==b;r['staged'][p]={'bytes':len(b),'sha256':sha(b)};save(out,r)
   r['completed']=True
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:save(out,r)
def launch():
 verify();s=read(K/'stage001.json');assert s['completed'] and s['controller_sha256']==sha(Path(__file__).read_bytes());out=K/'launch001.json';assert not out.exists()
 with connect() as f:
  for p,v in {**s['critical'],**s['staged']}.items():assert sha(get(f,p))==v['sha256']
  assert not any(n.lower().startswith(PREFIX) for n in names(f,'/E'))
  r={'utc':utc(),'requested':True,'automatic_retry':False,'hook':False,'windows_intended':True,'command':r'SITE EXEC E:\Applications\XWN16Boot836\default.xbe','expected_return':'No automatic return: normal Windows startup leaves desktop running'}
  with out.open('x') as stream:json.dump(r,stream,indent=2)
  f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['reply_uncertain']=type(e).__name__
  save(out,r);print(json.dumps(r))
def poll():
 out=K/sys.argv[2];assert out.parent==K and out.name.startswith('poll') and out.suffix=='.json' and not out.exists()
 r={'utc':utc(),'authenticated':False,'launch_requested':False}
 try:
  with connect(3) as f:
   p=R+'/owner836.json';assert sha(get(f,p))==read(K/'stage001.json')['staged'][p]['sha256'];names(f,R);r['authenticated']=True
 except Exception as e:r['unavailable_type']=type(e).__name__
 save(out,r);print(json.dumps(r))
def collect():
 assert read(K/'launch001.json')['requested'] and read(K/'dashboard001.json')['authenticated']
 out=K/'collection001.json';assert not out.exists();r={'completed':False,'utc':utc(),'hook':'none installed','reports':{}};save(out,r)
 try:
  with connect() as f:
   rows=names(f,'/E');reports=[n for n in rows if n.startswith(PREFIX) and n.endswith('.json')];assert 1<=len(reports)<=12
   for p,v in read(K/'stage001.json')['staged'].items():assert sha(get(f,p))==v['sha256']
   d=P/'collection001';d.mkdir()
   for n in sorted(reports):
    b=get(f,'/E/'+n);assert len(b)==rows[n]['bytes']<=32768;(d/n).write_bytes(b);r['reports'][n]={'bytes':len(b),'sha256':sha(b),'data':json.loads(b)}
   r['completed']=True;r['windows_boot_proved']=False
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:save(out,r)
if __name__=='__main__':
 assert sys.argv[1] in ['stage','launch','poll','collect'];globals()[sys.argv[1]]()
