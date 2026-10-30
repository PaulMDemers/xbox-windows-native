"""Create-only1.6 E installation. Windows boot executables remain absent until qualification."""
import datetime,ftplib,hashlib,io,json,os,socket,sys,time,zipfile
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn835/install001')
sys.path.insert(0,str(W/'outputs/demo-audio-level256'));from common001 import ticket,queue
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda b:hashlib.sha256(b).hexdigest();utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text())
ROOTS=['/E/winnt','/E/documents and settings','/E/program files','/E/Applications/XWN16Boot835']
def allowed(p):return any(p==r or p.startswith(r+'/') for r in ROOTS) and '..' not in p and '\\' not in p
class FTP(ftplib.FTP):
 def ntransfercmd(self,*a,**kw):
  s,n=super().ntransfercmd(*a,**kw);s.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1);return s,n
def names(f,path):
 assert path in ['/E','/E/Applications'] or allowed(path)
 f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
 rows=[];f.retrlines('LIST',rows.append);v=[s.split(None,8) for s in rows];assert all(len(s)==9 for s in v)
 return {s[8].lower():{'name':s[8],'directory':s[0][0]=='d','bytes':int(s[4])} for s in v if s[8] not in ['.','..']}
def get(f,path):
 assert allowed(path);b=io.BytesIO()
 def take(v):
  assert b.tell()+len(v)<=64*1024**2;b.write(v)
 f.retrbinary('RETR '+path,take,65536);return b.getvalue()
assert not P.exists() and not (K/'installation001.json').exists();P.mkdir(parents=True)
pkg=read(K/'package001.json');assert pkg['verified'];cap=read(W/'outputs/boot720-capacity834/collection001.json');assert cap['completed']
assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(cap['utc'])).total_seconds()<600
assert cap['e']['free_bytes']>pkg['allocated_bytes']+256*1024**2
r={'state':'preflight','started_utc':utc(),'windows_launch_requested':False,'console_C_accessed':False,'source_sha256':sha(Path(__file__).read_bytes()),'package_sha256':sha((K/'package001.json').read_bytes()),'space':require_space(P,20.05),'verified_files':0,'verified_bytes':0,'hook':False}
def save():
 p=K/'installation001.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(p)
save();fd=None;lock=queue/'boot720835-install-active.lock';f=None
try:
 ticket();fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);os.write(fd,str(P).encode());os.fsync(fd)
 archive=Path('E:/xwn343/bundle002/stock-e-1080i-001.zip');assert sha(archive.read_bytes())==pkg['archive_sha256']
 z=zipfile.ZipFile(archive);assert sha(z.read('MANIFEST.json'))==pkg['manifest_sha256']
 c=read(Path('C:/xwn820/connection.json'));assert c['host']=='192.168.50.66';f=FTP();f.connect(c['host'],timeout=15);f.login(c['user'],c['password'])
 r['before_e']=names(f,'/E');r['before_apps']=names(f,'/E/Applications')
 for root in ROOTS:
  parent,leaf=root.rsplit('/',1);assert leaf.lower() not in names(f,parent),('occupied root',root)
 assert all(allowed(p) for p in pkg['files']) and all(allowed(p) for p in pkg['directories'])
 assert len({p.lower() for p in pkg['files']})==len(pkg['files'])
 r['state']='installing';save();deadline=time.monotonic()+7200
 with (P/'writes.jsonl').open('xb',buffering=0) as journal:
  def record(kind,path,meta=None):
   assert time.monotonic()<deadline
   journal.write((json.dumps({'utc':utc(),'kind':kind,'path':path,'meta':meta})+'\n').encode());os.fsync(journal.fileno())
  for path in pkg['directories']:
   parent,leaf=path.rsplit('/',1);assert leaf.lower() not in names(f,parent)
   record('mkdir_intent',path);f.mkd(path);record('mkdir_done',path)
  seen={}
  for path,meta in sorted(pkg['files'].items()):
   ticket();parent,leaf=path.rsplit('/',1)
   if parent not in seen:seen[parent]=names(f,parent)
   assert leaf.lower() not in seen[parent]
   data=z.read('payload'+meta['archive_path']);assert len(data)==meta['bytes'] and sha(data)==meta['sha256']
   record('write_intent',path,{'bytes':len(data),'sha256':sha(data)})
   for at in range(0,max(1,len(data)),32768):f.storbinary(('STOR ' if at==0 else 'APPE ')+path,io.BytesIO(data[at:at+32768]),1024)
   assert get(f,path)==data,('readback mismatch',path)
   record('write_verified',path,{'bytes':len(data),'sha256':sha(data)});seen[parent][leaf.lower()]=True
   r['verified_files']+=1;r['verified_bytes']+=len(data);r['last_verified']=path
   if r['verified_files']%25==0:save()
  # Qualified binaries are still withheld. Never make this partial boot chain launchable.
  boot=names(f,ROOTS[-1]);assert not any(n in boot for n in ['default.xbe','freeldr.sys','rosload.exe'])
  e=names(f,'/E');apps=names(f,'/E/Applications')
  for root in ROOTS[:3]:e.pop(root.rsplit('/',1)[1].lower())
  apps.pop('xwn16boot835');assert e==r['before_e'] and apps==r['before_apps']
 r.update(state='payload_installed',completed_utc=utc(),ordinary_startup_unchanged=True,overwrite_count=0,boot_executables_present=False);save()
except BaseException as e:r.update(state='failed',error_type=type(e).__name__,error=str(e),quarantined=True);save();raise
finally:
 if f:f.close()
 if fd is not None:os.close(fd);lock.unlink()
print(json.dumps({'state':r['state'],'files':r['verified_files'],'windows_launch_requested':False}))
