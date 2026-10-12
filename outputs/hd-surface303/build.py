"""Fresh matched surface-bounds builds; never mutate the qualified parent."""
import datetime,hashlib,json,os,pathlib,shlex,shutil,subprocess,sys
K=pathlib.Path(__file__).resolve().parent; W=K.parents[1]
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
base=pathlib.Path('/home/paul/xbox-windows-native/build/hd-surface303-build001')
out=pathlib.Path('/mnt/d/xwn303/build001');assert not base.exists() and not out.exists()
space=require_space(base)
for c in space['checks']:assert c['free_bytes']-1024**3>=20*1024**3,'Projected build guard'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert read(K/'host001.json')['passed']
parent=pathlib.Path('/home/paul/xbox-windows-native/build/video-text-clip205-001/source')
old=read(W/'outputs/video-text-clip205/build-report.json');review=read(K/'source-review.json')
tree=subprocess.check_output(['git','-C',str(parent),'write-tree'],text=True).strip()
assert tree==old['source_tree']=='4e335dc7a23b4fc058db597a1dded0c098af3cb1'
assert sha(K/'0119-hd-surface-bounds.patch')==review['patch_sha256']
lock=read(W/'outputs/video-trace-reuse/inputs.json');rosbe=pathlib.Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
for n,h in lock['tool_sha256'].items():assert sha(rosbe/n)==h
out.mkdir(parents=True);base.mkdir();src=base/'source';src.mkdir()
r=dict(status='started',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,parent_tree=tree,tool_sha256=lock['tool_sha256'],patch_sha256=review['patch_sha256'],commands=[],cases={})
def run(args,**kw):
 r['commands'].append(list(map(str,args)));return subprocess.run(args,check=True,stdout=log,stderr=log,**kw)
try:
 with (out/'source.log').open('w') as log:
  p=subprocess.Popen(['git','-C',str(parent),'archive',tree],stdout=subprocess.PIPE,stderr=log)
  try:run(['tar','-x','-C',str(src)],stdin=p.stdout)
  finally:p.stdout.close()
  assert p.wait()==0
  run(['git','init','-q',str(src)]);run(['git','-C',str(src),'add','-A'])
  assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==tree
  for n,h in review['parent_source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h
  run(['git','-C',str(src),'apply','--index',str(K/'0119-hd-surface-bounds.patch')])
  for n,h in review['source_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h
  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()
 for name,enabled in [('control001','OFF'),('candidate001','ON')]:
  require_space(base)
  with (out/(name+'.log')).open('w') as log:
   defs=dict(old['builds'][1]['definitions']);assert defs['XWN_TEXT_BOUNDS']=='ON'
   defs['XWN_HD_SURFACE_BOUNDS']=enabled
   build=base/name;assert not build.exists()
   configure=['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+a+'='+b for a,b in defs.items()]
   compile=['cmake','--build',str(build),'--target','xwnown','--','-j4']
   script='set -e\n'+shlex.join(configure)+'\n'+shlex.join(compile)+'\n'
   (out/(name+'-commands.sh')).write_text(script)
   run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True)
   target=out/name;target.mkdir();p=target/'xwnown.dll'
   shutil.copyfile(build/'win32ss/drivers/displays/framebuf/xwnown.dll',p)
   r['cases'][name]=dict(definitions=defs,sha256=sha(p),bytes=p.stat().st_size,status='compiled')
   (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n');print(name,'compiled',flush=True)
 r['status']='compiled'
except Exception as e:r.update(status='failed',error=repr(e));raise
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r['logs']={p.name:sha(p) for p in out.glob('*.log')}
 (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
