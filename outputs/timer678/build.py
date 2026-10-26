"""Fresh host-only full firmware timer-probe integration; no console access."""
import datetime,hashlib,json,os,re,shutil,subprocess,sys,uuid
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
P=Path('/mnt/c/xwn674/source001');S=Path('/home/paul/xbox-windows-native/timer678-source001');B=Path('/mnt/c/xwn678/build001')
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not S.exists() and not B.exists() and not (K/'build001.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,deployed=False,commands=[],source_pins={})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space_source']=require_space(S,20.125);r['space_output']=require_space(B,20.05)
 parent=json.loads((W/'outputs/watched674/build001.json').read_text())
 assert subprocess.check_output(['git','-C',str(P),'write-tree'],text=True).strip()==parent['tree']
 assert not subprocess.check_output(['git','-C',str(P),'diff','--name-only'])
 r['parent_tree']=parent['tree'];S.mkdir();B.mkdir(parents=True);(B/'tmp').mkdir()
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)==parent['compiler_sha256']
 r['compiler_sha256']=sha(cc);env=dict(os.environ,TMPDIR=str(B/'tmp'))
 def run(name,args,timeout=90,cwd=None):
  r['commands'].append([str(a) for a in args]);save()
  v=subprocess.run(args,capture_output=True,timeout=timeout,cwd=cwd,env=env)
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr)
  assert v.returncode==0,(name,v.returncode,v.stderr[-1500:]);return v.stdout.decode()
 run('export',['git','-C',str(P),'checkout-index','--all','--prefix='+str(S)+'/'])
 D=S/'drivers/diag657'
 for path,name in [(K/'export.c','export.c'),(W/'outputs/timer675/probe.c','probe675.c'),(W/'outputs/timer675/probe.h','probe.h'),(W/'outputs/timer675/native.c','native675.c')]:
  (D/name).write_bytes(path.read_bytes());r['source_pins'][str(path.relative_to(W))]=sha(path)
 # Keep each new record's identity distinct while preserving the original codec.
 r['attempt']=uuid.uuid4().hex;r['build_id']=hashlib.sha256(json.dumps({'parent':r['parent_tree'],'pins':r['source_pins']},sort_keys=True).encode()).hexdigest()
 old=(D/'identity657.h').read_text();config=re.search(r'static const uint8_t SourceIP657\[4\].*?static const uint16_t Port657=.*?;',old,re.S);assert config
 nums=lambda b:','.join('0x%02x'%v for v in b)
 (D/'identity657.h').write_text('static const struct xwn655_identity Identity657={{'+nums(bytes.fromhex(r['attempt']))+'},{'+nums(bytes.fromhex(r['build_id']))+'}};\n'+config[0]+'\n')
 r['identity_header_sha256']=sha(D/'identity657.h')
 for path,needle,extra in [(D/'Makefile','signal672.o',' probe675.o native675.o'),(S/'Makefile','$(TOPDIR)/obj/signal672.o',' $(TOPDIR)/obj/probe675.o $(TOPDIR)/obj/native675.o')]:
  t=path.read_text();assert t.count(needle)==1;path.write_text(t.replace(needle,needle+extra))
 run('init',['git','init','-q',str(S)]);run('index',['git','-C',str(S),'add','-f','.']);r['tree']=run('tree',['git','-C',str(S),'write-tree']).strip()
 host=B/'host';host.mkdir();(host/'gcc').write_text('#!/bin/sh\nexec '+str(cc)+' "$@"\n');(host/'gcc').chmod(0o755);env['PATH']=str(host)+':'+env['PATH']
 r['flags']=parent['flags']
 run('build',['make','all','CC='+str(cc),'GITREV=xwn633-480p','EXTRA_CROM_CFLAGS='+r['flags'],'LDFLAGS-ROM=-s -S -T '+str(S/'scripts/ldscript-crom.ld')+' -Map='+str(B/'image-crom.map')],300,S)
 for src,dst in [('xbe/xromwell.xbe','default.xbe'),('obj/image-crom.elf','image-crom.elf')]:shutil.copyfile(S/src,B/dst)
 run('binary',['objcopy','-O','binary',str(B/'image-crom.elf'),str(B/'image-crom.bin')])
 run('symbols',['nm','-n',str(B/'image-crom.elf')]);run('disassembly',['objdump','-d',str(B/'image-crom.elf')])
 r['unchanged_objects']={}
 for name in ['xwn_hd_adapter','xwn_hd_profile','xwn_hd_native','net656_core','net656_native','net656_admission','encode657','bridge657','indicate658','phase669','irq669','pci','BootLibrary','BootStartup','BootInterrupts','BootEEPROM','cputools','microcode','BootResetAction']:
  for section in ['.text','.rodata']:
   values=[]
   for tag,root in [('old',P),('new',S)]:
    dest=B/(name+'-'+tag+section);run(name+'-'+tag+section,['objcopy','-O','binary','--only-section='+section,str(root/'obj'/(name+'.o')),str(dest)]);values.append(dest.read_bytes())
   assert values[0]==values[1],(name,section);r['unchanged_objects'][name+section]=hashlib.sha256(values[0]).hexdigest()
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()}
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('Full firmware built; host-only, no console qualification:',r['passed'])
