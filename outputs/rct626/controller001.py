"""Cold-start recording attempt: ordinary Windows first, manual game launch later.
No new payload or startup hook. Retained624 helper is verified by exact identity.
"""
import importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn626/physical001')
sys.dont_write_bytecode=True
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py');pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read
KIT='/E/xwn624-kit';GAME='/E/xwn586-kit/game'
def save(n,r):m.write_json(K/n,r)
def budget():assert shutil.disk_usage('C:/').free-100*1024**2>20*1024**3
def snapshot():
 budget();out=K/'before001.json';assert not out.exists() and not P.exists()
 ready=read(K/'readiness001.json');assert ready['dashboard_ready'] and ready['off_ten_seconds_confirmed']
 prev=read(K.parent/'rct625/final001.json');assert prev['closed'] and prev['cleanup_passed'] and not prev['runner_output_present']
 old=read(K.parent/'rct625/collection001.json');assert old['completed'] and old['hook_removed']
 q=read(K.parent/'rct624/final001.json');assert q['passed'] and q['closed']
 P.mkdir(parents=True);r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,launch_requested=False)
 save(out.name,r)
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');r['startup']=m.startup(f)
  assert 'xwn624' not in {n.lower() for n in m.names(f,'/E')}
 for n,row in old['files'].items():
  with m.connect(timeout=15) as f:
   a=m.get(f,n);b=m.get(f,n);assert a==b and m.sha(a)==row['sha256'],n
  r['files'][n]=m.keep(P/'before',n,a);save(out.name,r)
 assert r['files'][KIT+'/play624.exe']['sha256']==q['launcher_sha256']
 r.update(completed=True,ended_utc=m.utc(),mode='720p',prior_closed625_contents_exact=True,automatic_game_launch=False,source_pins={str(p.resolve()):m.sha(p.read_bytes()) for p in [Path(__file__),K/'readiness001.json',K.parent/'rct625/final001.json',K.parent/'rct624/final001.json']});save(out.name,r)
 print('Fresh cold-start baseline captured; no writes or hook')
def launch():
 b=read(K/'before001.json');assert b['completed'];out=K/'launch001.json';assert not out.exists()
 for n,h in b['source_pins'].items():assert m.sha(Path(n).read_bytes())==h,n
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');assert m.startup(f)==b['startup'];assert 'xwn624' not in {n.lower() for n in m.names(f,'/E')}
  for n,row in b['files'].items():assert m.sha(m.get(f,n))==row['sha256'],n
  pair.request_once(f,out,dict(ordinary_launcher=True,automatic_game_launch=False,automatic_restart=False,temporary_hook_installed=False,console_C_accessed=False,before_sha256=m.sha((K/'before001.json').read_bytes())))
 print('Ordinary Windows requested once; wait for desktop before manual RCT launch')
def collect():
 budget();assert read(K/'launch001.json')['requested'];out=K/'collection001.json';assert not out.exists();before=read(K/'before001.json')
 r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,temporary_hook_installed=False)
 save(out.name,r)
 with m.connect(timeout=15) as f:
  # This attempt installs no hook; any unexpected startup entry stops collection.
  r['startup']=m.startup(f);m.baseline(f,'720p');r['protected_code_exact']=True
  r['save_listing']=m.names(f,GAME+'/Saved Games');r['result_listing']={}
  if 'xwn624' in {n.lower() for n in m.names(f,'/E')}:
   r['result_listing']=m.names(f,'/E/xwn624');assert set(r['result_listing'])<={'runner.txt','registry.bin'}
  save(out.name,r)
 paths=list(dict.fromkeys(list(before['files'])+[GAME+'/Saved Games/'+n for n,v in r['save_listing'].items() if not v['directory']]+['/E/xwn624/'+n for n in r['result_listing']]))
 for n in paths:
  with m.connect(timeout=15) as f:
   a=m.get(f,n);b=m.get(f,n);assert a==b,n
  r['files'][n]=m.keep(P/'after',n,a);save(out.name,r)
 r.update(completed=True,ended_utc=m.utc(),normal_shutdown_proved=False,collection_scope='Selected OS hives/events, original launcher/startup, RCT executable/config, all saves and owned recording output; no full FATX allocation audit');save(out.name,r)
 print('Recording evidence collected; no temporary hook existed')
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ('snapshot','launch','collect');globals()[sys.argv[1]]()
