"""Fresh watched Notepad persistence sequence; no remote file writes or hooks."""
import importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; P=Path('C:/xwn588')
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py')
pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair);m=pair.m
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
SAVE='/E/xwn588.txt'
EXPECTED=b'Xbox save test 588\r\n'

def verify():
 m.ticket();r=read(K/'host001.json');assert r['passed']
 for p,h in r['pins'].items():assert m.sha(Path(p).read_bytes())==h,p

def snapshot(label):
 verify();assert label in ('before','after1','after2')
 out=K/(label+'.json');folder=P/label;assert not out.exists() and not folder.exists()
 if label!='before':assert read(K/f'launch{label[-1]}.json')['requested']
 assert all(shutil.disk_usage(d+':/').free-(96*1024**2 if d=='C' else 0)>=20*1024**3 for d in ('C','E'))
 folder.mkdir();r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
 m.write_json(out,r)
 try:
  with m.connect(timeout=15) as f:
   m.baseline(f,'720p');r['startup_listing']=m.startup(f);r['ordinary_code_exact']=True
   r['save_listed']=SAVE.rsplit('/',1)[1].lower() in {n.lower() for n in m.names(f,'/E')}
   if label=='before':assert not r['save_listed'],'Refuse existing test file'
  for n in pair.FILES+([SAVE] if r['save_listed'] else []):
   b=m.cold_pair(n,r,out);assert b is not None
   r['files'][n]=m.keep(folder,n,b);m.write_json(out,r)
  r.update(completed=True,ended_utc=m.utc())
 except BaseException as e:r['error_type']=type(e).__name__;raise
 finally:m.write_json(out,r)
 print(json.dumps(dict(completed=True,files=len(r['files']),save_present=r['save_listed'])))

def launch(ordinal):
 verify();assert ordinal in (1,2)
 before=read(K/('before.json' if ordinal==1 else 'after1.json'));assert before['completed']
 if ordinal==2:
  assert read(K/'audit1.json')['hives_clean']
  assert read(K/'observer1.json')['normal_restart_reported']
  assert before['save_listed']
 out=K/f'launch{ordinal}.json';assert not out.exists()
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');assert m.startup(f)==before['startup_listing']
  for n,row in before['files'].items():assert m.sha(m.get(f,n))==row['sha256'],n
  pair.request_once(f,out,dict(ordinal=ordinal,original_launcher=True,
    before_sha256=m.sha((K/('before.json' if ordinal==1 else 'after1.json')).read_bytes()),
    temporary_hook_installed=False,remote_file_writes=[],manual_restart_required=True,
    console_C_accessed=False,automatic_retry_allowed=False))
 print('One launch recorded; do not resend accepted or uncertain request.')

if __name__=='__main__':
 assert len(sys.argv)==2
 a=sys.argv[1]
 if a in ('before','after1','after2'):snapshot(a)
 elif a in ('launch1','launch2'):launch(int(a[-1]))
 else:raise ValueError('Unknown action')
