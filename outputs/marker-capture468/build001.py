"""Capture-only child of exact466; no status predicate or success-path change."""
import hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent; P=Path('/mnt/c/xwn466/build001'); O=Path('/mnt/c/xwn468/build001')
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.environ.get('XWN_BUILD_LEASE')=='held' and not O.exists() and not (K/'build001.json').exists()
assert shutil.disk_usage('/mnt/c').free-32*1024**2>=20*1024**3
parent=json.loads((K.parent/'marker-handoff466/build001.json').read_text())
for name,v in parent['files'].items():
 p=Path(name); assert sha(p.read_bytes())==v['sha256'],name
cc=Path('/usr/bin/x86_64-linux-gnu-gcc-12')
assert sha(cc.read_bytes())==parent['source_pins'][str(cc)]
source=(P/'xbeboot.S').read_text().replace('466','468')
edits=[]
def sub(old,new):
 global source
 assert source.count(old)==1,old
 source=source.replace(old,new);edits.append((old,new))
sub('    mov [refusal_record+68], eax\n    cmp dword ptr [diag_closed], 0','''    mov [refusal_record+68], eax
    // Copy the completed or untouched marker BEFORE any cleanup/kernel call.
    // No new hardware read, no retry, and no mutation of the live marker.
    cld
    mov esi, offset before_marker_record
    mov edi, offset refusal_marker
    mov ecx, 24
    rep movsd
refusal_snapshot_ready:
    cmp dword ptr [diag_closed], 0''')
sub('    push 96\n    push offset refusal_record','    push 192\n    push offset refusal_record')
sub('    cmp dword ptr [refusal_iosb+4], 96','    cmp dword ptr [refusal_iosb+4], 192')
sub('    .ascii "R468"\n    .long 1, 96, 0x46800101','    .ascii "R468"\n    .long 2, 192, 0x46800101')
sub('    .ascii "DONE"\n    .long 1, 0x46800101, 96','''refusal_marker:
    .zero 96
    .ascii "DONE"
    .long 2, 0x46800101, 192''')
reconstructed=source
for old,new in reversed(edits):
 assert reconstructed.count(new)==1
 reconstructed=reconstructed.replace(new,old)
assert reconstructed.replace('468','466')==(P/'xbeboot.S').read_text()
O.mkdir(parents=True)
(O/'xbeboot.S').write_text(source)
for name in ['xbe.S','font.S','payload.bin']:shutil.copyfile(P/name,O/name)
commands=[]
r=dict(status='building',physical_access=False,parent_sha256=parent['sha256'],reconstructed_parent_exact=True,
 source_edits=edits,source_pins={str(p):sha(p.read_bytes()) for p in [K/'build001.py',P/'xbeboot.S',cc]})
def save():(K/'build001.json').write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for cmd in [[str(cc),'-m32','-DASSEMBLER','-c','xbeboot.S','-o','xbeboot.o'],['ld','-m','elf_i386','-Ttext','0x10000','-e','_start','xbeboot.o','-o','wrapper.elf'],['objcopy','-O','binary','wrapper.elf','wrapper.bin']]:
  commands.append(cmd)
  with (O/'build.log').open('a') as f:subprocess.run(cmd,cwd=O,stdout=f,stderr=f,check=True,timeout=30)
 symbols=subprocess.check_output(['nm','-n','wrapper.elf'],cwd=O,text=True)
 (O/'symbols.txt').write_text(symbols)
 ws={v[2]:int(v[0],16) for line in symbols.splitlines() if len(v:=line.split())==3}
 prefix=(O/'wrapper.bin').read_bytes();assert len(prefix)==0x3000
 original=(P/'default.xbe').read_bytes();xbe=bytearray(prefix+original[0x3000:]);xbe[:4096]=original[:4096]
 xbe[0x348+36:0x348+56]=hashlib.sha1(struct.pack('<I',len(xbe)-4096)+xbe[4096:]).digest()
 assert xbe[0x3000:]==original[0x3000:] and len(xbe)==len(original)
 assert ws['refusal_marker']-ws['refusal_record']==80 and ws['refusal_handle']-ws['refusal_record']==192
 assert ws['gdt_48_base']+4-ws['blentry']==224 and ws['ptr_newloc']-ws['blentry']==74
 (O/'default.xbe').write_bytes(xbe)
 r.update(status='compiled',sha256=sha(xbe),bytes=len(xbe),payload_bytes=parent['payload_bytes'],payload_sha256=parent['payload_sha256'],wrapper_symbols=ws,stub_symbols=parent['stub_symbols'],commands=commands,payload_byte_identical=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:
 r['files']={str(p):dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in O.iterdir() if p.is_file()};save()
