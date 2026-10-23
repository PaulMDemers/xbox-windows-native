"""Fresh leased host-only i386 integration ELF; PCI helpers are UD2 boundaries."""
import datetime,hashlib,json,os,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];B=Path('/mnt/c/xwn670/host003')
S=Path('/mnt/c/xwn667/source001');out=K/'host003.json'
assert sys.platform=='linux' and os.environ.get('XWN_BUILD_LEASE')=='held'
assert not B.exists() and not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=False,physical_access=False,new_XBE=False,commands=[],inputs={})
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 sys.path.insert(0,str(W/'tools'));from build_space import require_space
 r['space']=require_space(B,minimum_gib=20.05);B.mkdir(parents=True);D=B/'source';D.mkdir();(B/'tmp').mkdir()
 inputs=list(K.glob('*.c'))+list(K.glob('*.h'))+list(K.glob('*.S'))+list(K.glob('*.ld'))+[Path(__file__)]
 inputs += [W/'outputs/terminal669'/n for n in ['phase.h','phase.c','irq.S']]
 inputs += [S/'drivers/diag656'/n for n in ['native.c','admission.c','admission.h','nic.c','nic.h']]
 inputs += [S/'drivers/diag657'/n for n in ['packet.c','packet.h','receipt.h','indication.c','indication.h']]
 for p in inputs:
  assert not (D/p.name).exists();(D/p.name).write_bytes(p.read_bytes());r['inputs'][p.name]=dict(path=str(p),sha256=sha(p))
 r['legacy_headers']={str(p.relative_to(S)):sha(p) for p in S.rglob('*.h') if '.git' not in p.parts}
 cc=Path('/usr/bin/gcc-12').resolve();assert sha(cc)=='e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
 r['tools']={n:sha(Path(subprocess.check_output(['which',n],text=True).strip()).resolve()) for n in ['ld','objcopy','objdump','nm']};r['compiler_sha256']=sha(cc)
 def run(name,args):
  r['commands'].append([str(a) for a in args]);save()
  v=subprocess.run(args,capture_output=True,timeout=90,env=dict(os.environ,TMPDIR=str(B/'tmp')))
  (B/(name+'.stdout')).write_bytes(v.stdout);(B/(name+'.stderr')).write_bytes(v.stderr);assert v.returncode==0,(name,v.returncode)
  return v.stdout
 flags=['-m32','-march=i686','-O2','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-fno-stack-protector','-nostdinc','-isystem',str(S/'include'),'-I'+str(D)]
 flags += ['-I'+str(S/d) for d in ['grub','include','.','fs/cdrom','fs/fatx','fs/grub','lib/eeprom','lib/crypt','drivers/video','drivers/ide','drivers/flash','lib/misc','boot_xbe','lib/font','startuploader','drivers/cpu','lib/jpeg','menu/actions','menu/textmenu','menu/iconmenu']]
 names=['integration','phase','native','admission','nic','packet','indication']
 for n in names:run(n,[str(cc),*flags,'-c',str(D/(n+'.c')),'-o',str(B/(n+'.o'))])
 for n in ['irq','host_boundary']:run(n,[str(cc),'-m32','-c',str(D/(n+'.S')),'-o',str(B/(n+'.o'))]);names.append(n)
 run('link',['ld','-m','elf_i386','-T',str(D/'host.ld'),*[str(B/(n+'.o')) for n in names],'-o',str(B/'integration.elf')])
 assert not run('undefined',['nm','-u',str(B/'integration.elf')])
 run('flat',['objcopy','-O','binary',str(B/'integration.elf'),str(B/'integration.bin')])
 run('symbols',['nm','-n',str(B/'integration.elf')]);run('disassembly',['objdump','-d',str(B/'integration.elf')])
 r['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in B.iterdir() if p.is_file()};r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps(dict(passed=r['passed'],physical_access=False,new_XBE=False)))
