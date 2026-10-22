"""One ordinary720p recovery control after failed645. No remote file writes or test hook."""
import importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn646/physical001')
s=importlib.util.spec_from_file_location('previous642',K.parent/'windows480p642/physical.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
m=b.m;session=b.session;read=b.read
COMMAND=r'SITE EXEC E:\Applications\XWNEBoot\default.xbe'
def check(f):
 m.ticket();m.baseline(f,'720p');b.startup(f)
 assert m.sha(m.get(f,m.TARGET))=='6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
 assert read(K.parent/'display-selector645/collection001.json')['restored720p']
 assert read(K.parent/'display-selector645/closure001.json')['closed']
def prepare():
 assert not P.exists() and not (K/'preparation001.json').exists()
 assert shutil.disk_usage('C:/').free-128*1024**2>=20*1024**3
 m.ticket();P.mkdir(parents=True)
 r=dict(utc=m.utc(),completed=False,remote_file_writes=False,test_hook=False,before={})
 out=K/'preparation001.json';m.write_json(out,r)
 try:
  with m.connect(timeout=15) as f:
   check(f)
   for n in b.protected()+m.MUTABLE+['/E/xwn480p642/input.txt']:
    data=m.get(f,n);assert data==m.get(f,n);r['before'][n]=m.keep(P/'before',n,data);m.write_json(out,r)
   assert m.get(f,'/E/xwn480p642/input.txt') in [b'XBOX480',b'XBOX480\r\n']
   r['source_pins']={p.name:m.sha(p.read_bytes()) for p in K.glob('*.py')}
  r['completed']=True
 except BaseException as e:r['failure_type']=type(e).__name__;raise
 finally:m.write_json(out,r)
def request_once(f,out):
 r=dict(utc=m.utc(),requested=True,command=COMMAND,automatic_retry=False,ordinary720p=True,test_hook=False)
 with out.open('x') as stream:json.dump(r,stream,indent=2)
 f.sock.settimeout(20)
 try:r['reply']=f.sendcmd(COMMAND)
 except Exception as e:r['reply_uncertain']=type(e).__name__
 m.write_json(out,r)
def launch():
 s=read(K/'preparation001.json');assert s['completed']
 assert read(K/'host001.json')['controller_sha256']==m.sha(Path(__file__).read_bytes())
 for n,h in s['source_pins'].items():assert m.sha((K/n).read_bytes())==h
 with m.connect(timeout=15) as f:
  check(f)
  for n,v in s['before'].items():assert m.sha(m.get(f,n))==v['sha256'],n
  request_once(f,K/'launch001.json')
def collect():
 assert read(K/'launch001.json')['requested'];out=K/'collection001.json';assert not out.exists()
 r=dict(utc=m.utc(),completed=False,after={},test_hook=False,remote_file_writes=False)
 m.write_json(out,r);s=read(K/'preparation001.json')
 try:
  with m.connect(timeout=15) as f:
   check(f)
   for n in s['before']:
    data=m.get(f,n);assert data==m.get(f,n);r['after'][n]=m.keep(P/'after',n,data);m.write_json(out,r)
   r['protected_unchanged']=all(r['after'][n]['sha256']==s['before'][n]['sha256'] for n in b.protected()+['/E/xwn480p642/input.txt'])
  r.update(completed=True,dashboard_returned=True,ended_utc=m.utc())
 except BaseException as e:r['failure_type']=type(e).__name__;raise
 finally:m.write_json(out,r)
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['prepare','launch','collect'];session();globals()[sys.argv[1]]()
