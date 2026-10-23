"""Fresh leased HOST-ONLY prototype build. Never produces or stages an XBE."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/mnt/c/xwn669/host001');out=K/'host001.json'
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,host_only=True,new_XBE=False,commands=[])
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05);B.mkdir(parents=True);(B/'source').mkdir();(B/'tmp').mkdir()
 for p in K.iterdir():
  if p.suffix in ['.c','.h','.S','.py']:(B/'source'/p.name).write_bytes(p.read_bytes())
 r['source_pins']={p.name:sha(p) for p in (B/'source').iterdir()}
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['compiler_sha256']=sha(cc);env=dict(os.environ,TMPDIR=str(B/'tmp'))
 def run(name,args):
  r['commands'].append([str(a) for a in args]);save();v=subprocess.run(args,capture_output=True,timeout=90,env=env)
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr);assert v.returncode==0,(name,v.returncode)
  return v.stdout
 run('host-compile',[str(cc),'-std=c99','-O1','-Wall','-Wextra','-Werror','-g','-fsanitize=address,undefined','-fno-pie','-no-pie',str(B/'source/phase.c'),str(B/'source/test.c'),'-o',str(B/'test')])
 r['tests']=json.loads(run('host-tests',[str(B/'test')]))
 flags=['-m32','-march=i686','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-nostdinc','-isystem','/mnt/c/xwn667/source001/include','-I'+str(B/'source')]
 run('core32',[str(cc),*flags,'-c',str(B/'source/phase.c'),'-o',str(B/'phase.o')])
 assert not run('core-undefined',['nm','-u',str(B/'phase.o')])
 run('irq32',[str(cc),'-m32','-c',str(B/'source/irq.S'),'-o',str(B/'irq.o')])
 run('irq-link',['ld','-m','elf_i386','-Ttext=0x100000','-e','irq_enter669',str(B/'irq.o'),'-o',str(B/'irq.elf')])
 run('irq-flat',['objcopy','-O','binary',str(B/'irq.elf'),str(B/'irq.bin')])
 run('irq-disasm',['objdump','-d',str(B/'irq.elf')]);run('core-disasm',['objdump','-dr',str(B/'phase.o')])
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()};r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],tests=r.get('tests'),new_XBE=False)))
