"""Append tested entry gate to exact497. Private compile only; no deployment."""
import datetime,hashlib,json,os,re,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn497/build002');H=K.parent/'entry-receipt498'
O=Path('/mnt/c/xwn499/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
assert sha(P/'default.xbe')=='09e3043c10837f20a3aef7d2b94ac54145b047ff9fafe02fb111fd25425b9274'
old=(P/'default.xbe').read_bytes();prior=json.loads((K.parent/'d3d-scene497/build002.json').read_text())
host=json.loads((H/'host001.json').read_text());assert host['passed'] and host['closed']
assert sha(H/'entry.S')==host['source_pins']['entry.S']
for p,v in prior['files'].items():assert sha(Path(p))==v['sha256'],p
sources=['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S']
gcc=Path('/usr/bin/x86_64-linux-gnu-gcc-12')
toolpaths=[gcc,Path(subprocess.check_output([str(gcc),'-print-prog-name=cc1'],text=True).strip())]
toolpaths += [Path('/usr/bin')/n for n in ['as','ld','objcopy','objdump','readelf','nm']]
pins=[P/'default.xbe',*[P/n for n in sources],H/'entry.S',H/'host001.json',K/'build001.py',*toolpaths]
for t in toolpaths:
 deps=subprocess.check_output(['ldd',str(t)],text=True)
 pins += [Path(x) for x in re.findall(r'(?:=>\s+|^\s*)(/[^\s]+)',deps,re.M)]
pins=list(dict.fromkeys(pins))
O.mkdir(parents=True)
r=dict(started=utc(),status='building',physical_access=False,deployed=False,
 inputs={str(p):sha(p) for p in pins},commands=[],source_reconstruction=True)
def save():(K/'build001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run(argv):
 r['commands'].append(argv);save()
 with (O/'build.log').open('ab') as f:subprocess.run(argv,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
save()
try:
 for p in pins:shutil.copyfile(p,O/('input-'+str(len(list(O.glob('input-*')))).zfill(3)))
 changes=0
 for n in sources:
  b=(P/n).read_bytes();c=b.replace(b'XWNBoot497a',b'XWNBoot499a')
  assert c.replace(b'XWNBoot499a',b'XWNBoot497a')==b
  changes+=b.count(b'XWNBoot497a')
  if n=='xbeboot.S':c+=b'\n.set entry498_continue, _start\n#include "entry.S"\n'
  (O/n).write_bytes(c)
 assert changes==4
 gate=(H/'entry.S').read_bytes();assert gate.count(b'XWNBoot498a')==1
 (O/'entry.S').write_bytes(gate.replace(b'XWNBoot498a',b'XWNBoot499a'))
 run([str(gcc),'-m32','-nostdinc','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
 run(['/usr/bin/ld','-m','elf_i386','-Ttext','0x10000','-e','entry498_gate','xbeboot.o','-o','wrapper.elf'])
 run(['/usr/bin/objcopy','-O','binary','wrapper.elf','wrapper.bin'])
 # Independently relocatable copy for the reviewer to resolve every code/data relocation.
 run(['/usr/bin/as','--32','entry.S','-o','entry.o'])
 symbols=subprocess.check_output(['/usr/bin/nm','-n','wrapper.elf'],cwd=O,text=True)
 (O/'symbols.txt').write_text(symbols)
 sym={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
 for n,v in prior['wrapper_symbols'].items():
  if n not in ['_edata','_end','__bss_start']:assert sym[n]==v,n
 assert sym['entry498_continue']==sym['_start']==0x11100
 assert sym['entry498_gate']>=0x10000+len(old)
 b=bytearray((O/'wrapper.bin').read_bytes());assert not any(b[0x3000:0x84000])
 b[:4096]=old[:4096];b[0x3000:0x84000]=old[0x3000:0x84000]
 assert struct.unpack_from('<I',b,0x128)[0]^0xa8fc57ab==0x11100
 for off,v in [(0x10c,len(b)),(0x128,sym['entry498_gate']^0xa8fc57ab),(0x350,len(b)-4096),(0x358,len(b)-4096)]:struct.pack_into('<I',b,off,v)
 b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 expected=bytearray(old.replace(b'XWNBoot497a',b'XWNBoot499a'));assert len(expected)==len(old)
 allowed=set()
 for lo,hi in [(0x10c,0x110),(0x128,0x12c),(0x350,0x354),(0x358,0x35c),(0x36c,0x380)]:allowed.update(range(lo,hi))
 assert all(b[i]==expected[i] or i in allowed for i in range(len(old)))
 assert b.count(b'XWNBoot499a')==5 and b.count(b'XWNBoot497a')==0
 (O/'default.xbe').write_bytes(b)
 (O/'disassembly.txt').write_bytes(subprocess.check_output(['/usr/bin/objdump','-dr','-Mintel','wrapper.elf'],cwd=O))
 assert all(sha(Path(p))==h for p,h in r['inputs'].items())
 r.update(status='compiled',sha256=sha(O/'default.xbe'),bytes=len(b),wrapper_symbols=sym,
  original_code_addresses_unchanged=True,original_prefix_expected_exact=True,
  payload_byte_exact=b[0x3000:0x84000]==old[0x3000:0x84000],
  gate_source_sha256=sha(O/'entry.S'),header_allowed_ranges=[[min(allowed),max(allowed)]],
  actual_header_changes=[i for i in range(4096) if b[i]!=old[i]])
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()}
 r['finished']=utc();save()
