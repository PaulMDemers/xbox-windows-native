"""Pin the compiled checkpoint, actual callers, XBE section and SDK closure."""
import hashlib,json,re,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;b=json.loads((k/'build005.json').read_text());out=Path(b['path'])
sha=lambda data:hashlib.sha256(data).hexdigest()
for n,pin in b['outputs'].items():assert sha((out/n).read_bytes())==pin['sha256'],n
for n,pin in b['source'].items():assert sha((out/'input'/n).read_bytes())==pin,n
for n,pin in {**b['sdk_before'],**b['sdk_header_closure_before']}.items():
    assert sha((out/'sdk-inputs'/n).read_bytes())==pin,n
symbols={m[0]:int(m[1],16) for m in re.findall(r'^\s+[0-9a-fA-F]{4}:[0-9a-fA-F]{8}\s+(\S+)\s+([0-9a-fA-F]{16})\s', (out/'main.map').read_text(),re.M)}
required=['_checkpoint271','_record271','_main','_stop','_idle','_capture','_setup_draw','_program','_draw','_enable','_sources',
          '_pb_Head','_pb_Tail','_pb_Size','_pb_Put','_pb_DmaUserAddr','_pb_FifoChannelID','_pb_FifoHTAddr','_pb_GrCtxID','_pb_GrCtxInst','_pb_GrCtxTableInst']
assert all(n in symbols for n in required)
x=(out/'bin/default.xbe').read_bytes();assert x[:4]==b'XBEH'
u=lambda offset:struct.unpack_from('<I',x,offset)[0]
base=u(0x104);count=u(0x11c);headers=u(0x120)-base;assert count==4
sections=[]
for i in range(count):
    flags,va,size,raw,length,name,refs,head,tail=struct.unpack_from('<9I',x,headers+56*i)
    assert raw+length<=len(x)
    end=x.index(b'\0',name-base);label=x[name-base:end].decode()
    sections.append(dict(name=label,flags=flags,va=va,virtual_size=size,raw=raw,raw_size=length,sha256=sha(x[raw:raw+length])))
def read(va,n):
    matches=[s for s in sections if s['va']<=va and va+n<=s['va']+s['raw_size']];assert len(matches)==1
    s=matches[0];o=s['raw']+va-s['va'];return x[o:o+n]
entry=symbols['_checkpoint271'];body=read(entry,19)
assert body.hex()=='8b44240c8b4c24048b542408894a0c894214c3'
exe=Path('C:/msys64/mingw64/bin/llvm-objdump.exe')
d=subprocess.run([str(exe),'-d','--x86-asm-syntax=intel',str(out/'main.exe')],capture_output=True,timeout=60)
assert d.returncode==0;dis=d.stdout.decode();(out/'review-disassembly.txt').write_text(dis)
calls=[]
for line in dis.splitlines():
    if re.search(r'\bcall\s+0x'+format(entry,'x')+r'\b',line):
        m=re.match(r'\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)',line);assert m,line
        addr=int(m[1],16);opcode=bytes.fromhex(m[2]);assert len(opcode)==5 and opcode[0]==0xe8
        assert addr+5+struct.unpack_from('<i',opcode,1)[0]==entry and read(addr,5)==opcode
        calls.append(dict(va=addr,bytes=opcode.hex(),preceding32=read(addr-32,32).hex(),instruction=line.strip()))
assert len(calls)==3,calls
vs=(out/'vs.inl').read_text();ps=(out/'ps.inl').read_text();flat=(out/'flat.inl').read_text()
assert '//const c[0] = 1' in vs and '// 6 instructions, 0 R-regs' in vs
assert all(f'STAGE{i}_2D_PROJECTIVE' in ps for i in range(4))
assert 'SET_SHADER_STAGE_PROGRAM' not in flat
main=(out/'main.c').read_text()
assert 'const float ones[4]={1,1,1,1}' in main
assert 'p=pb_push1(p,NV097_SET_SHADER_STAGE_PROGRAM,0);' in main
assert 'attrs[]={0,9},counts[]={4,4}' in main
result=dict(binary_review_passed=True,guest_executed=False,live_attestation=False,release_installed=False,
    xbe_sha256=sha(x),exe_sha256=sha((out/'main.exe').read_bytes()),iso_sha256=sha((out/'owned-texture271.iso').read_bytes()),
    checkpoint=dict(va=entry,bytes=body.hex(),sha256=sha(body),abi='cdecl phase at ESP+4, record at ESP+8, cookie at ESP+12; stores phase/cookie then returns'),
    callsites=calls,symbols={n:symbols[n] for n in required},record_bytes=1612,sections=sections,
    sdk_header_count=len(b['sdk_header_closure_before']),sdk_pins_count=len(b['sdk_before']),
    tools=dict(objdump_sha256=sha(exe.read_bytes()),xbe_layout_header_sha256=sha(Path('C:/nxdk/tools/cxbe/Xbe.h').read_bytes())),
    shader_review=['All four projective texture stages emitted; incoming TEX0 supplied at hardware9 with explicit z0/w1.',
                   'Generated vertex constant c0=1 is explicitly uploaded at hardware96.',
                   'Flat fragment program has no texture program; native code explicitly zeros previous texture program and stage dependencies.',
                   'Three additive combiner stages produce RGB channel sums; all selected input channel sums are below255. Runtime pixel comparison remains required.'],
    disassembly_sha256=sha((out/'review-disassembly.txt').read_bytes()),
    limits='Static compiled bytes and ABI only. Runtime must prove loaded XBE/kernel/address translations and actual application object/texture ownership; no host address is a live fact yet.')
p=k/'binary-review005.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:result[n] for n in ['binary_review_passed','xbe_sha256','checkpoint','record_bytes','sdk_header_count','sdk_pins_count']},indent=2))
