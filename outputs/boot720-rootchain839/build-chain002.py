"""Build pinned stock-E FreeLoader and mode-retaining Xromwell; no deployment."""
import datetime,hashlib,json,os,shlex,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/home/paul/xbox-windows-native/boot720839-source001');O=Path('/mnt/c/xwn839/chain002')
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists()
sys.path.insert(0,str(W/'tools'));from build_space import require_space
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
r={'passed':False,'physical_access':False,'space':require_space(B,21.5),'commands':[]};O.mkdir(parents=True)
def save():(K/'chain002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 source=read(K/'source001.json');r['source_record_sha256']=sha(K/'source001.json')
 for label,tree in source['trees'].items():
  assert subprocess.check_output(['git','-C',str(B/label),'write-tree'],text=True).strip()==tree
  assert not subprocess.check_output(['git','-C',str(B/label),'diff','--name-only'])
 rosbe=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1');lock=read(W/'outputs/video-trace-reuse/inputs.json')
 for n,h in lock['tool_sha256'].items():assert sha(rosbe/n)==h
 r['tool_sha256']=lock['tool_sha256'];cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['gcc12_sha256']=sha(cc);defs=dict(read(W/'outputs/stock-boot334/build001.json')['definitions']);defs['XWN_RETAIN_720_835']='ON';r['definitions']=defs
 src=B/'reactos';build=B/'nt5'
 configure=['cmake','-S',str(src),'-B',str(build),'-G','Ninja','-DCMAKE_TOOLCHAIN_FILE='+str(src/'toolchain-gcc.cmake')]+['-D'+k+'='+v for k,v in defs.items()]
 compile=['cmake','--build',str(build),'--target','freeldr','rosload','--','-j4']
 script='set -e\n'+shlex.join(configure)+'\n'+shlex.join(compile)+'\n';(O/'commands.sh').write_text(script);r['commands']+=[configure,compile];save()
 with (O/'nt5.log').open('w') as log:subprocess.run([str(rosbe/'RosBE.sh'),str(src),'0','i386'],input=script,text=True,stdout=log,stderr=log,check=True,timeout=900)
 for rel,name in [('boot/freeldr/freeldr/freeldr.sys','freeldr.sys'),('boot/freeldr/freeldr/rosload.exe','rosload.exe')]:shutil.copyfile(build/rel,O/name)
 host=O/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
 env=dict(os.environ,PATH=str(host)+':'+os.environ['PATH']);csrc=B/'cromwell'
 flags='-DXWN_PHYSICAL_PREFLIGHT=1 -DXWN_HD_RESERVATION=1 -DXWN_RETAIN_720_835=1';r['cromwell_flags']=flags
 args=['make','all','CC='+str(cc),'GITREV=xwn839-retain720','EXTRA_CROM_CFLAGS='+flags,'LDFLAGS-ROM=-s -S -T '+str(csrc/'scripts/ldscript-crom.ld')+' -Map='+str(O/'image-crom.map')];r['commands'].append(args);save()
 with (O/'cromwell.log').open('w') as log:subprocess.run(args,cwd=csrc,env=env,stdout=log,stderr=log,check=True,timeout=300)
 shutil.copyfile(csrc/'obj/image-crom.elf',O/'image-crom.elf')
 subprocess.run(['objcopy','-O','binary',str(O/'image-crom.elf'),str(O/'image-crom.bin')],check=True)
 for name,args in [('symbols',['nm','-n']),('disassembly',['objdump','-d'])]:
  with (O/(name+'.txt')).open('wb') as f:subprocess.run(args+[str(O/'image-crom.elf')],stdout=f,check=True)
 r['passed']=True
except BaseException as e:r['error']=repr(e);raise
finally:
 r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in O.iterdir() if p.is_file()}
 r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save();print('boot chain build:',r['passed'])
