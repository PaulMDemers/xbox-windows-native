"""Build dormant native binding in a new retained651 export; never launch it."""
import datetime,hashlib,json,os,subprocess,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/mnt/c/xwn651/source001');S=Path('/mnt/c/xwn656/source002');B=Path('/mnt/c/xwn656/build002')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not S.exists() and not B.exists() and not (K/'native002.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='preflight',physical_access=False,native_hook_installed=False,launchable_diagnostic=False,
       started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'native002.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05)
 assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()=='2fda813f3b8109dfc6b70f6d37e21d2cf9a66d55'
 assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 S.mkdir(parents=True);B.mkdir(parents=True);(B/'tmp').mkdir()
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc);env=dict(os.environ,TMPDIR=str(B/'tmp'))
 r['source_pins']={p.name:sha(p) for p in K.iterdir() if p.suffix in ('.c','.h','.py')}
 def run(name,args,timeout=90,cwd=None):
  r.setdefault('commands',[]).append([str(a) for a in args]);save()
  x=subprocess.run(args,capture_output=True,timeout=timeout,env=env,cwd=cwd)
  (B/(name+'.stdout')).write_bytes(x.stdout);(B/(name+'.stderr')).write_bytes(x.stderr)
  assert x.returncode==0,(name,x.returncode)
  return x.stdout.decode()
 flags=['-std=c99','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-pie','-no-pie']
 run('guard-compile',[str(cc),*flags,str(K/'admission.c'),str(K/'test_admission.c'),'-o',str(B/'guard')])
 r['admission_tests']=json.loads(run('guard',[str(B/'guard')]))
 run('export',['git','-C',str(P),'checkout-index','--all','--prefix='+str(S)+'/'])
 D=S/'drivers/diag656';D.mkdir()
 for name in ('nic.c','nic.h','admission.c','admission.h','native.c'):(D/name).write_bytes((K/name).read_bytes())
 for stem,body in (('net656_core','nic.c'),('net656_native','native.c'),('net656_admission','admission.c')):
  (D/(stem+'.c')).write_text('#include "'+body+'"\n')
 (D/'Makefile').write_text('O_TARGET := net656_core.o net656_native.o net656_admission.o\ninclude $(TOPDIR)/Rules.make\n')
 make=S/'Makefile';text=make.read_text();marker='OBJECTS-CROM = $(TOPDIR)/obj/BootStartup.o'
 assert text.count(marker)==1
 make.write_text(text.replace(marker,marker+'\nOBJECTS-CROM += $(TOPDIR)/obj/net656_core.o $(TOPDIR)/obj/net656_native.o $(TOPDIR)/obj/net656_admission.o'))
 make=S/'drivers/Makefile';text=make.read_text();assert 'subdir' in text
 make.write_text(text.replace('include $(TOPDIR)/Rules.make','subdir += diag656\ninclude $(TOPDIR)/Rules.make'))
 run('init',['git','init','-q',str(S)]);run('index',['git','-C',str(S),'add','-f','.'])
 r['tree']=run('tree',['git','-C',str(S),'write-tree']).strip()
 host=B/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755)
 env['PATH']=str(host)+':'+env['PATH']
 r['flags']=json.loads((W/'outputs/readback651/build001.json').read_text())['flags']
 run('build',['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+r['flags'],'LDFLAGS-ROM=-s -S -T '+str(S/'scripts/ldscript-crom.ld')+' -Map='+str(B/'image-crom.map')],timeout=300,cwd=S)
 for src,dst in [('xbe/xromwell.xbe','DO-NOT-LAUNCH.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(S/src,B/dst)
 r['unchanged_objects']={}
 for stem in ('xwn_hd_native','xwn_hd_adapter','xwn_hd_profile','forcedeth'):
  for section in ('.text','.rodata'):
   pair=[]
   for tag,root in (('old',P),('new',S)):
    out=B/(stem+'-'+tag+section);run(stem+'-'+tag+section,['objcopy','-O','binary','--only-section='+section,str(root/'obj'/(stem+'.o')),str(out)]);pair.append(out.read_bytes())
   assert pair[0]==pair[1],(stem,section);r['unchanged_objects'][stem+section]=hashlib.sha256(pair[0]).hexdigest()
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()}
 r['status']='compiled-dormant'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(status=r['status'],admission_tests=r.get('admission_tests'))))
