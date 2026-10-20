"""Recording-session preparation using original720p launcher and retained retail assets.
Private session config supplies credentials. No dashboard C access. No retries.
"""
import importlib.util,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn625/physical001')
sys.dont_write_bytecode=True
s=importlib.util.spec_from_file_location('pair532',K.parent/'windows-pair532/controller.py');pair=importlib.util.module_from_spec(s);s.loader.exec_module(pair)
m=pair.m;read=pair.read
KIT='/E/xwn624-kit';GAME='/E/xwn586-kit/game';HOOK=m.START+'/xwn625.cmd';USED=KIT+'/startup-used625.cmd'
FILES=pair.FILES+['/E/documents and settings/Win2K/NTUSER.DAT',GAME+'/RCT.EXE',GAME+'/Data/Game.cfg',GAME+'/Data/CSS0.DAT']
def hook():return b'@echo off\r\nif exist C:\\xwn624 goto done\r\nC:\\xwn624-kit\\play624.exe\r\n:done\r\nexit\r\n'
def save(n,r):m.write_json(K/n,r)
def budget():assert shutil.disk_usage('C:/').free-100*1024**2>20*1024**3
def snapshot():
 budget();out=K/'before001.json';assert not out.exists() and not P.exists();P.mkdir(parents=True)
 r=dict(completed=False,utc=m.utc(),files={},remote_writes=[],console_C_accessed=False,launch_requested=False)
 save(out.name,r)
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');r['startup']=m.startup(f);r['kit_listing']=m.names(f,'/E/xwn586-kit');r['game_listing']=m.names(f,GAME);r['save_listing']=m.names(f,GAME+'/Saved Games')
  assert 'xwn624-kit' not in {n.lower() for n in m.names(f,'/E')} and m.get(f,HOOK,True) is None
 paths=FILES+[GAME+'/Saved Games/'+n for n,v in r['save_listing'].items() if not v['directory']]
 for n in paths:
  with m.connect(timeout=15) as f:
   a=m.get(f,n);b=m.get(f,n);assert a==b,n
  r['files'][n]=m.keep(P/'before',n,a);save(out.name,r)
 expected=read(K.parent/'rct596/cleanup-apply001.json')['verified']['/E/winnt/system32/config/software']
 assert r['files']['/E/winnt/system32/config/software']['sha256']==expected['sha256'],'Console state changed since cleanup; review before writes'
 assert r['files'][GAME+'/RCT.EXE']['sha256']=='bdfebd64383b231de0252fe0726523d1c45aa2c4da919c2d7ed8bfb7aaa05c76'
 r.update(completed=True,ended_utc=m.utc(),software_matches596_cleanup=True,mode='720p');save(out.name,r)
 print('Recording baseline captured; no console writes or launch')
def stage():
 budget();b=read(K/'before001.json');assert b['completed'];q=read(K.parent/'rct624/final001.json');assert q['passed'] and q['closed']
 exe=Path('C:/xwn624/build002/play624.exe').read_bytes();assert m.sha(exe)==q['launcher_sha256']
 r=dict(completed=False,utc=m.utc(),writes=[],staged={},source_pins={},console_C_accessed=False)
 out=K/'stage001.json';assert not out.exists();save(out.name,r)
 for p in [Path(__file__),K.parent/'rct624/final001.json',K/'before001.json']:r['source_pins'][str(p.resolve())]=m.sha(p.read_bytes())
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');assert m.startup(f)==b['startup']
  for n,row in b['files'].items():assert m.sha(m.get(f,n))==row['sha256'],n
  assert not {'xwn624-kit','xwn624'}&{n.lower() for n in m.names(f,'/E')}
  r['writes'].append(dict(action='mkdir',path=KIT));save(out.name,r);f.mkd(KIT)
  owner=json.dumps(dict(case=625,purpose='interactive windowed RCT recording',launcher_sha256=m.sha(exe),automatic_restart=False)).encode()
  for n,data in [(KIT+'/owner.json',owner),(KIT+'/play624.exe',exe),(HOOK,hook())]:
   r['writes'].append(dict(action='store',path=n));save(out.name,r);m.put(f,n,data);assert m.get(f,n)==data
   r['staged'][n]=dict(bytes=len(data),sha256=m.sha(data));save(out.name,r)
  assert m.sha(m.get(f,m.NORMAL))==b['files'][m.NORMAL]['sha256']
 r.update(completed=True,ended_utc=m.utc(),hook_installed=True);save(out.name,r)
 print('Interactive launcher staged; no timer, restart or game modification')
def launch():
 st=read(K/'stage001.json');b=read(K/'before001.json');ready=read(K/'readiness001.json');assert st['completed'] and ready['dashboard_ready']
 out=K/'launch001.json';assert not out.exists()
 for n,h in st['source_pins'].items():assert m.sha(Path(n).read_bytes())==h,n
 with m.connect(timeout=15) as f:
  m.baseline(f,'720p');rows=m.names(f,m.START);assert {n.lower() for n in rows}<={'xwnsetup.cmd','desktop.ini','xwn625.cmd'}
  assert 'xwn624' not in {n.lower() for n in m.names(f,'/E')}
  for n,row in {**b['files'],**st['staged']}.items():assert m.sha(m.get(f,n))==row['sha256'],n
  pair.request_once(f,out,dict(ordinary_launcher=True,recording_session=True,automatic_restart=False,game_timeout=False,console_C_accessed=False,stage_sha256=m.sha((K/'stage001.json').read_bytes())))
 print('One launch requested; never retry this attempt. Await user observation.')
if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ('snapshot','stage','launch');globals()[sys.argv[1]]()
