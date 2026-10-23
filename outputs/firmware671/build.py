"""Fresh leased full firmware integration. Build only; never deploy/launch."""
import datetime,hashlib,json,os,re,shutil,subprocess,sys,uuid
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/mnt/c/xwn667/source001');S=Path('/mnt/c/xwn671/source001');B=Path('/mnt/c/xwn671/build001');out=K/'build001.json'
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not S.exists() and not B.exists() and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(status='preflight',physical_access=False,deployed=False,diagnostic_only=True,commands=[],source_pins={})
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05)
 r['parent_tree']=subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()
 assert r['parent_tree']=='f8c2b7aadf8f8537546428af471910b479671660'
 assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 S.mkdir(parents=True);B.mkdir(parents=True);(B/'tmp').mkdir()
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc);env=dict(os.environ,TMPDIR=str(B/'tmp'))
 def run(name,args,timeout=90,cwd=None):
  r['commands'].append([str(a) for a in args]);save();v=subprocess.run(args,capture_output=True,timeout=timeout,env=env,cwd=cwd)
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr);assert v.returncode==0,(name,v.returncode)
  return v.stdout.decode()
 run('export',['git','-C',str(P),'checkout-index','--all','--prefix='+str(S)+'/'])
 D=S/'drivers/diag657';inputs=[K/'export.c',K/'build.py']
 for base,names in [(W/'outputs/terminal669',['phase.c','phase.h','irq.S']),(W/'outputs/native670',['integration.c','integration.h'])]:inputs += [base/n for n in names]
 for p in inputs:
  r['source_pins'][str(p.relative_to(W))]=sha(p)
  if p.suffix!='.py':(D/p.name).write_bytes(p.read_bytes())
 # Unique externally assigned identity token; not a self-hash. Network config
 # is read from the retained configured private header, never hardcoded here.
 r['attempt']=uuid.uuid4().hex
 manifest=dict(parent_tree=r['parent_tree'],source_pins=r['source_pins']);r['identity_manifest']=manifest
 r['build_id']=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
 old=(D/'identity657.h').read_text();config=re.search(r'static const uint8_t SourceIP657\[4\].*?static const uint16_t Port657=.*?;',old,re.S)
 assert config
 nums=lambda b:','.join('0x%02x'%v for v in b)
 header='static const struct xwn655_identity Identity657={{'+nums(bytes.fromhex(r['attempt']))+'},{'+nums(bytes.fromhex(r['build_id']))+'}};\n'+config[0]+'\n'
 (D/'identity657.h').write_text(header);r['identity_header_sha256']=sha(D/'identity657.h')
 for name,content in [('phase669.c','#include "phase.c"\n'),('integration670.c','#include "integration.c"\n')]: (D/name).write_text(content)
 (D/'irq669.S').write_bytes((D/'irq.S').read_bytes())
 objects='phase669.o integration670.o irq669.o'
 m=D/'Makefile';t=m.read_text();assert 'classify667.o' in t;m.write_text(t.replace('classify667.o','classify667.o '+objects))
 m=S/'Makefile';t=m.read_text();needle='OBJECTS-CROM += $(TOPDIR)/obj/classify667.o';assert needle in t
 m.write_text(t.replace(needle,needle+'\nOBJECTS-CROM += '+' '.join('$(TOPDIR)/obj/'+n for n in objects.split())))
 run('init',['git','init','-q',str(S)]);run('index',['git','-C',str(S),'add','-f','.']);r['tree']=run('tree',['git','-C',str(S),'write-tree']).strip()
 host=B/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755);env['PATH']=str(host)+':'+env['PATH']
 r['flags']=json.loads((W/'outputs/memory667/build001.json').read_text())['flags']
 run('build',['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+r['flags'],'LDFLAGS-ROM=-s -S -T '+str(S/'scripts/ldscript-crom.ld')+' -Map='+str(B/'image-crom.map')],300,S)
 for src,dst in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(S/src,B/dst)
 run('binary',['objcopy','-O','binary',str(B/'image-crom.elf'),str(B/'image-crom.bin')])
 run('symbols',['nm','-n',str(B/'image-crom.elf')]);run('disassembly',['objdump','-d',str(B/'image-crom.elf')])
 r['unchanged_objects']={}
 for name in ['xwn_hd_adapter','xwn_hd_profile','net656_core','net656_native','net656_admission','xwn_hd_native','encode657','bridge657','indicate658','pci','BootLibrary','BootStartup','BootInterrupts','BootEEPROM','cputools','microcode','BootResetAction']:
  for section in ['.text','.rodata']:
   values=[]
   for tag,root in [('old',P),('new',S)]:
    dest=B/(name+'-'+tag+section);run(name+'-'+tag+section,['objcopy','-O','binary','--only-section='+section,str(root/'obj'/(name+'.o')),str(dest)]);values.append(dest.read_bytes())
   assert values[0]==values[1],(name,section);r['unchanged_objects'][name+section]=hashlib.sha256(values[0]).hexdigest()
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()}
 r['status']='compiled-host-only-unqualified'
except BaseException as e:r.update(status='failed',failure=repr(e));raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(r['status'])
