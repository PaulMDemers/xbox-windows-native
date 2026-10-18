"""Compile a private appended handoff witness; never deploy or launch."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent; O=Path('/mnt/c/xwn485/build001'); P=Path('/mnt/c/xwn482/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-16*1024**2>=20*1024**3
assert sha(P/'xbeboot.S')=='2a846de7ffda32b97db3af47701b7beef8389fcf9b001b3c9c3f873049467e44'
assert sha(P/'default.xbe')=='13a6dac524242722c370227a7a3ed9e49037d4822103ed749a6dafc8f7c359db'
old=(P/'default.xbe').read_bytes(); tail=(len(old)+4095)&~4095
base=(P/'xbeboot.S').read_text(); source=base.replace('482','485')
anchor='diag_marker_ready:\n    popad\n    popfd\n    jmp edx'
replacement='diag_marker_ready:\n    jmp witness_entry'
assert source.count(anchor)==1
source=source.replace(anchor,replacement)
suffix=f'\n.org {tail:#x}\n#include "witness.S"\n'
source+=suffix
assert source.removesuffix(suffix).replace(replacement,anchor).replace('485','482')==base
O.mkdir(parents=True)
(O/'xbeboot.S').write_text(source)
for n in ['xbe.S','font.S']:shutil.copyfile(P/n,O/n)
shutil.copyfile(K/'witness.S',O/'witness.S')
r=dict(status='building',physical_access=False,deployed=False,source_reconstruction=True,tail_offset=tail,commands=[],inputs={str(p):sha(p) for p in [P/'default.xbe',P/'xbeboot.S',P/'xbe.S',P/'font.S',K/'witness.S',K/'build001.py',Path('/usr/bin/x86_64-linux-gnu-gcc-12')]})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for cmd in [['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'],['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'],['objcopy','-O','binary','wrapper.elf','wrapper.bin']]:
  r['commands'].append(cmd)
  with (O/'build.log').open('ab') as log:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=90)
 symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True);(O/'symbols.txt').write_text(symbols)
 sym={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
 prior=json.loads((K.parent/'d3d-depth482/build001.json').read_text())['wrapper_symbols']
 for n in ['blentry','newloc','ptr_newloc','gdt_48_base','kernel','_start','section_1_start']:assert sym[n]==prior[n],n
 b=bytearray((O/'wrapper.bin').read_bytes());assert sym['witness_entry']==0x10000+tail and not any(b[0x3000:tail])
 b[0x3000:len(old)]=old[0x3000:];b[:4096]=old[:4096]
 for off,value in [(0x10c,len(b)),(0x350,len(b)-4096),(0x358,len(b)-4096)]:struct.pack_into('<I',b,off,value)
 b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 assert b[0x3000:len(old)]==old[0x3000:]
 # Header differences are restricted to the two section extents, image size and digest.
 allowed=set(range(0x10c,0x110))|set(range(0x350,0x354))|set(range(0x358,0x35c))|set(range(0x36c,0x380))
 assert all(b[i]==old[i] or i in allowed for i in range(4096))
 (O/'default.xbe').write_bytes(b)
 r.update(status='compiled',sha256=sha(O/'default.xbe'),bytes=len(b),payload_byte_exact=True,original_loader_symbols_unchanged=True,wrapper_symbols=sym,header_changes=sorted(i for i in range(4096) if b[i]!=old[i]))
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
