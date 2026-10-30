"""PCI840: create-only stage, one bounded SITE, one collection. No Windows."""
import datetime,ftplib,hashlib,io,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn840')
sys.path.insert(0,str(W/'outputs/demo-audio-level256'));from common001 import ticket
R='/E/Applications/XWNEPci84000001'
sha=lambda b:hashlib.sha256(b).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
read=lambda p:json.loads(p.read_text())
def save(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def connect():
 ticket();c=read(Path('C:/xwn820/connection.json'));assert c['host']=='192.168.50.66'
 f=ftplib.FTP();f.connect(c['host'],timeout=15);f.login(c['user'],c['password']);return f
def names(f,path):
 assert path in ['/E','/E/Applications',R]
 f.cwd(path);assert f.pwd().replace('\\','/').rstrip('/').lower()==path.lower()
 rows=[];f.retrlines('LIST',rows.append)
 return {v[8]:{'dir':v[0][0]=='d','bytes':int(v[4])} for row in rows if len(v:=row.split(None,8))==9 and v[8] not in ['.','..']}
def get(f,path):
 assert path.startswith(R+'/');b=io.BytesIO()
 def take(v):
  assert b.tell()+len(v)<=1024*1024;b.write(v)
 f.retrbinary('RETR '+path,take,32768);return b.getvalue()
def verify():
 b=read(K/'build001.json');assert b['passed']
 for n,v in b['files'].items():assert sha((P/'build001'/n).read_bytes())==v['sha256']
 for n in ['main.c','report-path.h','Makefile']:assert (K/n).read_bytes()==(P/'build001'/n).read_bytes()
 return (P/'build001/bin/default.xbe').read_bytes()
def stage():
 data=verify();out=K/'stage001.json';assert not out.exists()
 r={'completed':False,'utc':utc(),'writes':[],'hook':False,'console_C_accessed':False};save(out,r)
 try:
  with connect() as f:
   r['before_e']=names(f,'/E');r['before_apps']=names(f,'/E/Applications');assert R.rsplit('/',1)[1].lower() not in {n.lower() for n in r['before_apps']}
   r['writes'].append(R);save(out,r);f.mkd(R)
   owner=json.dumps({'attempt':840,'purpose':'Read-only PCI configuration for Windows display discovery; automatic dashboard return','xbe_sha256':sha(data)}).encode()
   r['staged']={}
   for name,body in [('owner.json',owner),('default.xbe',data)]:
    path=R+'/'+name;r['writes'].append(path);save(out,r);f.storbinary('STOR '+path,io.BytesIO(body),32768)
    assert get(f,path)==body;r['staged'][path]={'bytes':len(body),'sha256':sha(body)};save(out,r)
   assert set(names(f,R))=={'owner.json','default.xbe'}
  r['completed']=True
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:save(out,r)
def launch():
 verify();s=read(K/'stage001.json');assert s['completed'];out=K/'launch001.json';assert not out.exists()
 f=connect()
 try:
  for p,v in s['staged'].items():assert sha(get(f,p))==v['sha256']
  assert set(names(f,R))=={'owner.json','default.xbe'}
  r={'utc':utc(),'requested':True,'command':r'SITE EXEC E:\Applications\XWNEPci84000001\default.xbe','automatic_retry':False,'hook':False}
  with out.open('x') as stream:json.dump(r,stream,indent=2)
  f.sock.settimeout(20)
  try:r['reply']=f.sendcmd(r['command'])
  except Exception as e:r['uncertain']=type(e).__name__
  save(out,r);print(json.dumps(r))
 finally:f.close()
def collect():
 assert read(K/'launch001.json')['requested'];out=K/'collection001.json';assert not out.exists()
 r={'completed':False,'utc':utc(),'hook':'none installed'};save(out,r)
 try:
  with connect() as f:
   assert 'pci.txt' in names(f,R)
   for p,v in read(K/'stage001.json')['staged'].items():assert sha(get(f,p))==v['sha256']
   data=get(f,R+'/pci.txt');assert len(data)<4096
   (P/'pci001.txt').write_bytes(data)
   r['report']=data.decode('ascii');r['sha256']=sha(data)
   lines=r['report'].splitlines();assert lines[0]=='XWN-PCI-840' and lines[-1]=='COMPLETE 840'
   assert len(lines)==50
   r['pci']=[]
   for line in lines[1:-1]:
    v=line.split();assert len(v)==5 and v[0]=='PCI'
    r['pci'].append({'bus':int(v[1]),'slot':int(v[2]),'offset':int(v[3],16),'value':int(v[4],16)})
   r['dashboard_authenticated']=True;r['completed']=True
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:save(out,r)
 print(json.dumps(r))
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['stage','launch','collect'];globals()[sys.argv[1]]()
