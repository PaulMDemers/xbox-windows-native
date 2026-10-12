"""Pin compiled HD diagnostic, ABI and caller; no live result is inferred."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent; out=Path('E:/xwn292/build003')
sha=lambda b:hashlib.sha256(b).hexdigest()
b=json.loads((k/'build003.json').read_text());assert b['compiled'] and b['sdk_unchanged']
for n,p in b['outputs'].items():assert sha((out/n).read_bytes())==p['sha256']
symbols={m[0]:int(m[1],16) for m in re.findall(r'^\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{16})\s',(out/'main.map').read_text(),re.M)}
x=(out/'bin/default.xbe').read_bytes();assert x[:4]==b'XBEH'
u=lambda o:struct.unpack_from('<I',x,o)[0]
base=u(0x104);count=u(0x11c);table=u(0x120)-base;sections=[]
assert base==0x10000 and count==4
for i in range(count):
    flags,va,size,raw,n,name=struct.unpack_from('<6I',x,table+56*i)
    assert raw+n<=len(x)
    label=x[name-base:x.index(b'\0',name-base)].decode()
    sections.append(dict(name=label,flags=flags,va=va,virtual_size=size,raw=raw,raw_size=n,sha256=sha(x[raw:raw+n])))
def read(va,n):
    s=next(s for s in sections if s['va']<=va and va+n<=s['va']+s['raw_size'])
    o=s['raw']+va-s['va'];return x[o:o+n]
entry=symbols['_checkpoint292'];body=read(entry,12)
# cdecl: load record and phase from stack, store record.phase (offset12), return.
assert body.hex()=='8b4424048b4c240889410cc3',body.hex()
p=subprocess.run(['C:/msys64/mingw64/bin/llvm-objdump.exe','-d','--x86-asm-syntax=intel',str(out/'main.exe')],capture_output=True,check=True,timeout=30)
(out/'disassembly.txt').write_bytes(p.stdout)
calls=[]
for line in p.stdout.decode().splitlines():
    if re.search(r'\bcall\s+0x'+format(entry,'x')+r'\b',line):
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)',line);assert m
        va=int(m[1],16);op=bytes.fromhex(m[2]);assert read(va,5)==op
        calls.append(dict(va=va,bytes=op.hex()))
assert len(calls)==4
source=(out/'input/main.c').read_text()
for forbidden in ['XVideoInit(', 'HalWriteSMBusValue(', 'HalReadWritePCISpace(', 'pb_init(', 'MmAllocateContiguousMemory(']:
    assert forbidden not in source
r=dict(passed=True,scope='Compiled standalone HD diagnostic only',checkpoint=dict(va=entry,bytes=body.hex()),
       calls=calls,record=symbols['_record292'],record_bytes=152,sections=sections,
       xbe_sha256=sha(x),iso_sha256=sha((out/'hd292.iso').read_bytes()),
       kernel_api_mode_setter=True,encoder_absence_means_unknown=True,
       reboot='HalRebootRoutine after fallback640x480 and 10-second pause; SDK calls can hang',guest_launched=False)
dest=k/'binary-review003.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','checkpoint','record','record_bytes']},indent=2))
