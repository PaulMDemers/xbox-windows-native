"""Exact504 child: historical entry plus JMP, five owned path literals and SHA1."""
import datetime,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/c/xwn504/build001');O=Path('/mnt/c/xwn510/build001');out=K/'build001.json'
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not out.exists() and not O.exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'));utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
prior=read(K.parent/'entry-binary504/build001.json');host=read(K/'host001.json');assert prior['status']=='compiled' and host['passed'] and host['closed']
for n,v in prior['files'].items():assert sha(Path(n))==v['sha256'],n
for n,v in host['files'].items():assert sha(Path(n))==v['sha256'],n
old=(P/'default.xbe').read_bytes();assert sha(P/'default.xbe')=='95a9734048b552fb531cd0c83138f9d7b332c8542573a4f49d5fa385fb0b4ece'
assert old[0x1100:0x1103]==b'\x9c\x8f\x05'
sources=['xbeboot.S','xbe.S','font.S','witness.S','context.S','capture.S','entry.S','combined.S','indicator.S']
tools=[Path('/usr/bin')/n for n in ['x86_64-linux-gnu-gcc-12','as','ld','objcopy','objdump','nm']]
for p in tools:assert sha(p)==prior['inputs'][str(p)]
O.mkdir(parents=True)
r=dict(started_utc=utc(),status='building',physical_access=False,deployed=False,inputs={str(p):sha(p) for p in [P/'default.xbe',*[P/n for n in sources],K/'build001.py',K/'host001.json',*tools]},commands=[])
def save():out.write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run(cmd):
 r['commands'].append(cmd);save()
 with (O/'build.log').open('ab') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=60)
try:
 anchor=b'_start:\n    pushfd\n    pop dword ptr [diag_record+16]'
 replacement=b'_start:\n.global entry510_trampoline\nentry510_trampoline:\n    jmp entry503_gate\n    .byte '+(','.join(hex(x) for x in old[0x1105:0x1107])).encode()
 changes=0
 for n in sources:
  src=(P/n).read_bytes();b=src.replace(b'XWNBoot504a',b'XWNBoot510a');changes+=src.count(b'XWNBoot504a')
  if n=='xbeboot.S':assert b.count(anchor)==1;b=b.replace(anchor,replacement)
  rebuilt=b.replace(replacement,anchor).replace(b'XWNBoot510a',b'XWNBoot504a');assert rebuilt==src,n
  (O/n).write_bytes(b)
 assert changes==5
 run(['x86_64-linux-gnu-gcc-12','-m32','-nostdinc','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'])
 run(['ld','-m','elf_i386','-Ttext','0x10000','-e','entry510_trampoline','xbeboot.o','-o','wrapper.elf'])
 run(['objcopy','-O','binary','wrapper.elf','wrapper.bin'])
 symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True);(O/'symbols.txt').write_bytes(symbols.encode())
 sy={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
 assert all(sy[n]==v for n,v in prior['wrapper_symbols'].items())
 assert sy['entry510_trampoline']==0x11100 and sy['entry503_gate']==0x94aff and sy['entry498_record']==0x95000
 b=bytearray((O/'wrapper.bin').read_bytes());assert len(b)==len(old) and not any(b[0x3000:0x84000])
 b[:4096]=old[:4096];b[0x3000:0x84000]=old[0x3000:0x84000]
 struct.pack_into('<I',b,0x128,0x11100^0xa8fc57ab)
 b[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(b)-4096)+b[4096:]).digest()
 expected=bytearray(old.replace(b'XWNBoot504a',b'XWNBoot510a'))
 expected[0x1100:0x1105]=b'\xe9'+struct.pack('<i',0x94aff-0x11105)
 struct.pack_into('<I',expected,0x128,0x11100^0xa8fc57ab)
 expected[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(expected)-4096)+expected[4096:]).digest()
 assert b==expected and b[0x1100:0x1105]==Path('/mnt/c/xwn510/host001/trampoline.bin').read_bytes()
 (O/'default.xbe').write_bytes(b)
 (O/'disassembly.txt').write_bytes(subprocess.check_output(['objdump','-d','-Mintel','wrapper.elf'],cwd=O))
 assert all(sha(Path(n))==h for n,h in r['inputs'].items())
 r.update(status='compiled',bytes=len(b),sha256=sha(O/'default.xbe'),wrapper_symbols=sy,source_anchor=anchor.decode(),source_replacement=replacement.decode(),
 source_parent_reconstruction=True,full_expected_binary_exact=True,stub_hex=b[0x1100:0x1105].hex(),all_original_symbol_addresses_unchanged=True,
 changed_offsets=[i for i in range(len(b)) if b[i]!=old[i]])
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r.update(finished_utc=utc(),files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in O.iterdir() if p.is_file()});save()
 print(json.dumps({n:r[n] for n in ['status','physical_access','deployed']}))
