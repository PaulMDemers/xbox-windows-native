"""Fresh export/reset diagnostic; building never stages or launches."""
import datetime,hashlib,json,os,subprocess,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/mnt/c/xwn656/source005');S=Path('/mnt/c/xwn657/source001');B=Path('/mnt/c/xwn657/build001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not S.exists() and not B.exists() and not (K/'build001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='preflight',physical_access=False,diagnostic_only=True,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05)
 assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()=='51fee92064ed330a642ed06a4ba6bda455e98e93'
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
 run('export',['git','-C',str(P),'checkout-index','--all','--prefix='+str(S)+'/'])
 D=S/'drivers/diag657';D.mkdir()
 for src,name in [(K/'export.c','export.c'),(W/'outputs/udp655/packet.c','packet.c'),(W/'outputs/receipt652/receipt.h','receipt.h'),(W/'outputs/receipt652/bridge.c','bridge.c'),(Path('/mnt/c/xwn657/identity657.h'),'identity657.h')]:
  (D/name).write_bytes(src.read_bytes());r.setdefault('import_pins',{})[str(src)]=sha(src)
 h=(W/'outputs/udp655/packet.h').read_text().replace('#include <stddef.h>\n','').replace('../receipt652/receipt.h','receipt.h')
 (D/'packet.h').write_text(h);(D/'nic.h').write_bytes((W/'outputs/net656/nic.h').read_bytes())
 for stem,body in [('export657','export.c'),('encode657','packet.c'),('bridge657','bridge.c')]:
  (D/(stem+'.c')).write_text('#include "'+body+'"\n')
 (D/'Makefile').write_text('EXTRA_CFLAGS := -Werror -Wno-unused-function -fno-pic -fno-pie\nO_TARGET := export657.o encode657.o bridge657.o\ninclude $(TOPDIR)/Rules.make\n')
 v=S/'drivers/video/xwn_hd_native.c';old=v.read_text()
 prefix=old[:old.index(' XwnDiag651Status=led651_show')]
 declaration='extern void XwnExport657(int,const struct xwn_hd_request *,const volatile struct xwn_hd_state *,const volatile struct xwn_trace649 *,const volatile struct readback651 *,const volatile struct readback651 *) __attribute__((noreturn));\n'
 prefix=prefix.replace('volatile unsigned XwnDiag651Status;',declaration+'volatile unsigned XwnDiag651Status;')
 v.write_text(prefix+' (void)mode;(void)comparison;\n XwnExport657(result,&r,&XwnHdState311,&XwnTrace649,&XwnReadback651Pre,&XwnReadback651Post);\n}\n#endif\n')
 make=S/'Makefile';t=make.read_text();marker='OBJECTS-CROM = $(TOPDIR)/obj/BootStartup.o';assert t.count(marker)==1
 make.write_text(t.replace(marker,marker+'\nOBJECTS-CROM += $(TOPDIR)/obj/export657.o $(TOPDIR)/obj/encode657.o $(TOPDIR)/obj/bridge657.o'))
 make=S/'drivers/Makefile';t=make.read_text();make.write_text(t.replace('include $(TOPDIR)/Rules.make','subdir += diag657\ninclude $(TOPDIR)/Rules.make'))
 run('init',['git','init','-q',str(S)]);run('index',['git','-C',str(S),'add','-f','.']);r['tree']=run('tree',['git','-C',str(S),'write-tree']).strip()
 host=B/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755);env['PATH']=str(host)+':'+env['PATH']
 r['flags']=json.loads((W/'outputs/net656/native005.json').read_text())['flags']
 run('build',['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+r['flags'],'LDFLAGS-ROM=-s -S -T '+str(S/'scripts/ldscript-crom.ld')+' -Map='+str(B/'image-crom.map')],timeout=300,cwd=S)
 for src,dst in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(S/src,B/dst)
 run('binary',['objcopy','-O','binary',str(B/'image-crom.elf'),str(B/'image-crom.bin')])
 r['unchanged_objects']={}
 for stem in ('xwn_hd_adapter','xwn_hd_profile','net656_core','net656_native','net656_admission'):
  for section in ('.text','.rodata'):
   pair=[]
   for tag,root in [('old',P),('new',S)]:
    out=B/(stem+'-'+tag+section);run(stem+'-'+tag+section,['objcopy','-O','binary','--only-section='+section,str(root/'obj'/(stem+'.o')),str(out)]);pair.append(out.read_bytes())
   assert pair[0]==pair[1],(stem,section);r['unchanged_objects'][stem+section]=hashlib.sha256(pair[0]).hexdigest()
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()};r['status']='compiled-unqualified'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(r['status'])
