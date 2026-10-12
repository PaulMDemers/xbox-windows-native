"""Matched reservation-only builds from prepared immutable source; no deployment."""
import datetime,hashlib,json,os,pathlib,shlex,shutil,subprocess,sys
K=pathlib.Path(__file__).resolve().parent;W=K.parents[1]
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
sys.path.insert(0,str(W/'tools'));from build_space import require_space
base=pathlib.Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001')
out=pathlib.Path('/mnt/e/xwn300/build001');assert not out.exists()
space=require_space(base);assert json.loads((K/'host001.json').read_text())['passed'];out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
review=read(K/'source-review002.json');src=base/'source'
for label,root in [('reactos',src),('cromwell',base/'cromwell')]:
 assert subprocess.check_output(['git','-C',str(root),'write-tree'],text=True).strip()==review['trees'][label]
 assert not subprocess.check_output(['git','-C',str(root),'diff','--name-only'])
 for n,pin in review['changes'].items():
  if n.startswith(label+'/'):assert sha(root/n.split('/',1)[1])==pin['after'],n
lock=read(W/'outputs/video-trace-reuse/inputs.json');rosbe=pathlib.Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1')
for n,h in lock['tool_sha256'].items():assert sha(rosbe/n)==h
cc=pathlib.Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
r=dict(status='building',started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),space=space,tool_sha256=lock['tool_sha256'],gcc12_sha256=sha(cc),source_review_sha256=sha(K/'source-review002.json'),commands=[],cases={})
def run(args,**kwargs):
 r['commands'].append(list(map(str,args)));return subprocess.run(args,check=True,stdout=log,stderr=log,**kwargs)
try:
 for name,enabled in [('control001','OFF'),('candidate001','ON')]:
  require_space(base)
  with (out/(name+'.log')).open('w') as log:
   defs=dict(lock['profiles']['video']['definitions']);defs.update(XBOX_NT5_SHARED_FRAMEBUFFER='ON',XBOX_NT5_HD_RESERVATION=enabled)
   build=base/name;assert not build.exists()
   configure=['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+a+'='+b for a,b in defs.items()]
   compile=['cmake','--build',str(build),'--target','freeldr','rosload','xboxvnt5','xboxbvidnt5','--','-j4']
   script='set -e\n'+shlex.join(configure)+'\n'+shlex.join(compile)+'\n'
   (out/(name+'-commands.sh')).write_text(script)
   run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True)
   target=out/name;target.mkdir();files={}
   for rel,n in [('boot/freeldr/freeldr/freeldr.sys','freeldr.sys'),('boot/freeldr/freeldr/rosload.exe','rosload.exe'),('win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.sys','xboxvnt5.sys'),('drivers/base/bootvid/xboxbvidnt5.dll','xboxbvid.dll')]:
    shutil.copyfile(build/rel,target/n);files[n]=dict(sha256=sha(target/n),bytes=(target/n).stat().st_size)
   csrc=base/('cromwell-'+name);assert not csrc.exists();csrc.mkdir()
   run(['git','-C',str(base/'cromwell'),'checkout-index','--all','--prefix='+str(csrc)+'/'])
   host=out/('host-'+name);host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
   env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH'])
   flags='-DXWN_PHYSICAL_PREFLIGHT'+(' -DXWN_HD_RESERVATION=1' if enabled=='ON' else '')
   run(['make','all','CC='+str(cc),'GITREV=9fc54d0-xwn-fboot','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(csrc/'scripts/ldscript-crom.ld')+' -Map='+str(target/'image-crom.map')],cwd=csrc,env=env)
   for rel,n in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf'),('obj/xbeboot.elf','xbeboot.elf')]:
    shutil.copyfile(csrc/rel,target/n);files[n]=dict(sha256=sha(target/n),bytes=(target/n).stat().st_size)
   r['cases'][name]=dict(definitions=defs,files=files,status='compiled')
   (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
   print(name,'compiled',flush=True)
 r['status']='compiled'
except Exception as e:r.update(status='failed',error=repr(e));raise
finally:
 r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 r['logs']={p.name:sha(p) for p in out.glob('*.log')}
 (K/'build001.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],flush=True)
