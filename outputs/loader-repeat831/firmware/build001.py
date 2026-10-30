"""Fresh full-image early entry integration. Host only; no deployment."""
import datetime,hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[2]
P=Path('/home/paul/xbox-windows-native/launcher677-validation002/default720/source')
S=Path('/home/paul/xbox-windows-native/xcal831-source001');B=Path('/mnt/c/xwn831/firmware001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not S.exists() and not B.exists() and not (K/'build001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,deployed=False,commands=[],source_pins={})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space_source']=require_space(S,20.125);r['space_output']=require_space(B,20.05)
 r['parent_tree']=subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()
 assert r['parent_tree']=='70c0a6c5aff82537f489e7d18410d5980fa797a7'
 assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 S.mkdir();B.mkdir(parents=True);(B/'tmp').mkdir()
 cc=Path('/usr/bin/gcc-12').resolve();r['compiler_sha256']=sha(cc)
 assert r['compiler_sha256']=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 env=dict(os.environ,TMPDIR=str(B/'tmp'))
 def run(name,args,timeout=60,cwd=None):
  r['commands'].append([str(a) for a in args]);save()
  v=subprocess.run(args,capture_output=True,timeout=timeout,cwd=cwd,env=env)
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr)
  assert v.returncode==0,(name,v.returncode,v.stderr[-1500:]);return v.stdout.decode()
 run('export',['git','-C',str(P),'checkout-index','--all','--prefix='+str(S)+'/'])
 D=S/'boot/xcal826';D.mkdir()
 for p in sorted(K.glob('*.[ch]')):
  (D/p.name).write_bytes(p.read_bytes());r['source_pins'][p.name]=sha(p)
 # Add the branch before any C-side initialization or legacy SMBus transaction.
 p=S/'boot/BootResetAction.c';t=p.read_text();needle='extern void BootResetAction ( void ) {'
 assert t.count(needle)==1
 p.write_text(t.replace(needle,needle+'\n#ifdef XWN_XCAL_ENTRY826\n\textern void XcalEntry826(void) __attribute__((noreturn));\n\tXcalEntry826();\n#endif\n'))
 # Unique object names avoid collisions with other native/config sources.
 names=['entry','transaction826','encoder','xcal_bus','gpu_preserving','led830']
 for n in names:shutil.copyfile(D/(n+'.c'),S/'boot'/('xcal826_'+n+'.c'))
 p=S/'boot/Makefile';t=p.read_text();t=t.replace('EXTRA_CFLAGS :=','EXTRA_CFLAGS := -I$(TOPDIR)/boot/xcal826')
 t=t.replace('O_TARGET :=','O_TARGET := '+' '.join('xcal826_'+n+'.o' for n in names));p.write_text(t)
 p=S/'Makefile';t=p.read_text();needle='OBJECTS-CROM += $(TOPDIR)/obj/BootResetAction.o';assert t.count(needle)==1
 p.write_text(t.replace(needle,needle+'\nOBJECTS-CROM += '+' '.join('$(TOPDIR)/obj/xcal826_'+n+'.o' for n in names)))
 run('init',['git','init','-q',str(S)]);run('index',['git','-C',str(S),'add','-f','.']);r['tree']=run('tree',['git','-C',str(S),'write-tree']).strip()
 host=B/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755);env['PATH']=str(host)+':'+env['PATH']
 r['flags']='-DXWN_HD_RESERVATION=1 -DXWN_HD_TIMING_720P=1 -DXWN_XCAL_ENTRY826=1'
 run('build',['make','all','CC='+str(cc),'GITREV=xwn830-entry','EXTRA_CROM_CFLAGS='+r['flags'],'LDFLAGS-ROM=-s -S -T '+str(S/'scripts/ldscript-crom.ld')+' -Map='+str(B/'image-crom.map')],300,S)
 for src,dst in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(S/src,B/dst)
 run('binary',['objcopy','-O','binary',str(B/'image-crom.elf'),str(B/'image-crom.bin')])
 run('symbols',['nm','-n',str(B/'image-crom.elf')]);run('disassembly',['objdump','-d',str(B/'image-crom.elf')])
 r['changed_integration']={n:sha(S/n) for n in ['Makefile','boot/Makefile','boot/BootResetAction.c']}
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('Full firmware built; host-only entry diagnostic:',r['passed'])
