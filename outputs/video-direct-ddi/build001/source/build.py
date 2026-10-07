"""Fresh direct-only display DDI build; no guest or physical launch."""
import hashlib,json,os,shlex,shutil,subprocess,sys,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'tools'))
from build_space import require_space
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
out=Path(sys.argv[1]);assert not out.exists();space=require_space(out);out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
base=ws/'outputs/video-trace-reuse';lock=read(base/'inputs.json');review=read(k/'patch-review.json');rosbe=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
for rel,h in lock['patch_sha256'].items():assert sha(ws/rel)==h
for rel,h in lock['tool_sha256'].items():assert sha(rosbe/rel)==h
assert sha(k/'0107-direct-nt5-display.patch')==review['patch_sha256']
for n,h in review['source_files'].items():assert sha(k/'display'/n)==h
manifest=ws/lock['manifest'];assert hashlib.sha256(json.dumps(read(manifest),sort_keys=True,separators=(',',':')).encode()).hexdigest()==lock['manifest_json_sha256']
r=dict(status='started',space=space,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),parent_tree=review['parent_tree'],patch_sha256=review['patch_sha256'],tool_sha256=lock['tool_sha256'],commands=[],builds=[])
def run(args,**kwargs):r['commands'].append(list(map(str,args)));return subprocess.run(args,check=True,**kwargs)
try:
 with (out/'build.log').open('w') as log:
  src=out/'source';run(['git','init','-q',str(src)],stdout=log,stderr=log)
  run(['git','-C',str(src),'fetch','--depth=1','/home/paul/xbox-windows-native/build/video-reuse-001/source',lock['base_commit']],stdout=log,stderr=log)
  run(['git','-C',str(src),'checkout','--detach','FETCH_HEAD'],stdout=log,stderr=log)
  run([sys.executable,str(ws/'tools/apply-series.py'),'--source',str(src),'--manifest',str(manifest)],stdout=log,stderr=log)
  run(['git','-C',str(src),'apply','--index',str(k.parent/'video-shared-framebuffer/0106-shared-uc-framebuffer.patch')],stdout=log,stderr=log)
  assert subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()==review['parent_tree']
  for n,h in review['original_files'].items():assert sha(src/'win32ss/drivers/displays/framebuf'/n)==h
  run(['git','-C',str(src),'apply','--index',str(k/'0107-direct-nt5-display.patch')],stdout=log,stderr=log)
  r['source_tree']=subprocess.check_output(['git','-C',str(src),'write-tree'],text=True).strip()
  for name,enabled in [('candidate001','ON')]:
   defs=dict(lock['profiles']['video']['definitions']);defs['XBOX_NT5_SHARED_FRAMEBUFFER']=enabled
   build=out/name;configure=['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+a+'='+b for a,b in defs.items()]
   compile=['cmake','--build',str(build),'--target','xwndir','--','-j4']
   script='set -e\n'+shlex.join(configure)+'\n'+shlex.join(compile)+'\n';(out/(name+'-commands.sh')).write_text(script)
   run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True,stdout=log,stderr=log)
   target=k/name;target.mkdir(exist_ok=False);(target/'artifacts').mkdir();files=[]
   for rel,n in [('win32ss/drivers/displays/framebuf/xwndir.dll','xwndir.dll')]:
    p=target/'artifacts'/n;shutil.copyfile(build/rel,p);files.append(dict(name=n,sha256=sha(p),bytes=p.stat().st_size))
   b=dict(case=name,definitions=defs,source_tree=r['source_tree'],files=files,patch_sha256=r['patch_sha256']);r['builds'].append(b);(target/'build.json').write_text(json.dumps(b,indent=2)+'\n')
  r['status']='compiled'
except Exception as e:r.update(status='failed',error=repr(e));raise
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(out/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');(k/'build-report.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
