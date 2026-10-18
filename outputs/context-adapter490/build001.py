"""Compile the reviewed adapter onto exact487; never deploy or launch."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn490/build001');P=Path('/mnt/c/xwn487/build001');H=Path('/mnt/c/xwn490/host001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
for name in ['host-build001.json','host-run001.json']:
 r=json.loads((K/name).read_text());assert r['passed']
 for p,v in r['files'].items():assert sha(Path(p))==v['sha256'],p
 for p,h in r.get('inputs',{}).items():assert sha(Path(p))==h,p
assert sha(P/'default.xbe')=='851a916de6454a8e100b98657d2f52625fedb1d12eb3e91d8dad932a3eab74ec'
old=(P/'default.xbe').read_bytes();tail=0x84000
base=(P/'xbeboot.S').read_text();suffix='\n#include "context.S"\ncapture490_begin:\n#include "capture.S"\ncapture490_end:\n'
source=base.replace('487','490')+suffix
assert source.removesuffix(suffix).replace('490','487')==base
O.mkdir(parents=True);(O/'xbeboot.S').write_text(source)
for n in ['xbe.S','font.S']:shutil.copyfile(P/n,O/n)
for n in ['witness.S','context.S','capture.S']:shutil.copyfile(H/n,O/n)
r=dict(status='building',physical_access=False,deployed=False,source_reconstruction=True,tail_offset=tail,commands=[],inputs={str(p):sha(p) for p in [P/'default.xbe',P/'xbeboot.S',P/'xbe.S',P/'font.S',H/'witness.S',H/'context.S',H/'capture.S',K/'build001.py',K/'host-build001.json',K/'host-run001.json',Path('/usr/bin/x86_64-linux-gnu-gcc-12')]})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for cmd in [['/usr/bin/x86_64-linux-gnu-gcc-12','-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'],['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'],['objcopy','-O','binary','wrapper.elf','wrapper.bin']]:
  r['commands'].append(cmd)
  with (O/'build.log').open('ab') as log:subprocess.run(cmd,cwd=O,stdout=log,stderr=log,check=True,timeout=90)
 symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True);(O/'symbols.txt').write_text(symbols)
 sym={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
 prior=json.loads((K.parent/'blend-precision487/build001.json').read_text())['wrapper_symbols']
 for n in ['blentry','newloc','ptr_newloc','gdt_48_base','kernel','_start','section_1_start','witness_entry']:assert sym[n]==prior[n],n
 b=bytearray((O/'wrapper.bin').read_bytes());assert sym['witness_entry']==0x10000+tail and not any(b[0x3000:tail])
 b[0x3000:tail]=old[0x3000:tail];b[:4096]=old[:4096]
 for off,value in [(0x10c,len(b)),(0x350,len(b)-4096),(0x358,len(b)-4096)]:struct.pack_into('<I',b,off,value)
 b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 assert b[0x3000:tail]==old[0x3000:tail]
 lo=sym['blentry']-0x10000;assert b[lo:lo+1024]==old[lo:lo+1024]
 lo=sym['capture490_begin']-0x10000;hi=sym['capture490_end']-0x10000
 assert hi-lo==313 and hashlib.sha256(b[lo:hi]).hexdigest()=='d5bed1052a1eeab8810e15f05734b2c9795d56641bf1ddb50e1a2618a808b196'
 allowed=set(range(0x10c,0x110))|set(range(0x350,0x354))|set(range(0x358,0x35c))|set(range(0x36c,0x380))
 assert all(b[i]==old[i] or i in allowed for i in range(4096))
 (O/'default.xbe').write_bytes(b)
 r.update(status='compiled',sha256=sha(O/'default.xbe'),bytes=len(b),payload_byte_exact=True,loader1024_byte_exact=True,capture313_byte_exact=True,original_loader_symbols_unchanged=True,wrapper_symbols=sym,header_changes=sorted(i for i in range(4096) if b[i]!=old[i]))
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()};save()
