# SPDX-License-Identifier: MIT
"""Static exact-byte interval map; never presents data as executable instructions."""
import datetime,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from capstone import Cs,CS_ARCH_X86,CS_MODE_32
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda b:hashlib.sha256(b).hexdigest()
q=read(K/'prepared001.json');p=Path(q['images']['1']['path']);b=p.read_bytes();assert sha(b)==q['images']['1']['sha256']
s=read(K.parent/'context-adapter490/build001.json')['wrapper_symbols']
t=read(K.parent/'busy-handoff471/build001.json')['stub_symbols']
m=Cs(CS_ARCH_X86,CS_MODE_32);rows=[]
def span(label,start,end,offset):
    code=b[offset:offset+end-start];ins=list(m.disasm(code,start))
    assert ins and ins[-1].address+ins[-1].size==end
    rows.append(dict(label=label,start=start,end=end,sha256=sha(code),
        instructions=[dict(address=i.address,bytes=i.bytes.hex(),mnemonic=i.mnemonic,operands=i.op_str) for i in ins]))
span('context return through file lifecycle',s['context490_post_return'],s['context490_bad_stack'],s['context490_post_return']-0x10000)
# The witness block includes the earlier pre-context file work as context; the
# post call and final comparisons/restore/jump are visible in its exact listing.
span('witness and final comparison/restore/jump',s['witness_entry'],s['witness_jump']+4,s['witness_entry']-0x10000)
span('privileged loader through final far jump',s['blentry'],s['newflash'],s['blentry']-0x10000)
span('Xromwell first jump',0x2600000,0x2600005,0x3000)
span('Xromwell setup before segment far jump',0x2600090,0x26000dd,0x3090)
span('Xromwell segments through stack detour',0x26000e0,0x26000f5,0x30e0)
span('post-stack existing marker caller and new hold',t['after_stack_stub'],t['after_stack_ready']+5,0x83000)
assert rows[-1]['instructions'][-4]['mnemonic']=='cli'
assert rows[-1]['instructions'][-3]['mnemonic']=='hlt'
# Reconstruct exact490 and independently require only namespace/digest/hold change.
base=Path('C:/xwn490/build001/default.xbe').read_bytes()
u=bytearray(b.replace(b'XWNBoot540a',b'XWNBoot490a'));o=q['hold_file_offset']
u[o:o+5]=bytes.fromhex(q['old_instruction_hex'])
import struct
u[0x36c:0x380]=hashlib.sha1(struct.pack('<I',len(u)-4096)+u[4096:]).digest()
assert bytes(u)==base
out=K/'interval-review001.json';assert not out.exists()
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=sha(b),
 intervals=rows,source_sha256=sha(Path(__file__).read_bytes()),physical_access=False,
 observations=['Last captured CPU epoch precedes context write/flush/close and final comparisons.',
 'Final original POPAD/POPFD/JMP enters CLI, paging disable, CR3 clear, descriptors/segments, full1MiB copy and far jump.',
 'Real Xromwell entry changes CR0/cache state, clears debug registers, copies its GDT and changes segments before stack setup.',
 'New halt occurs only after the existing post-stack marker reports both transactions complete; no original continuation executes.',
 'Earlier physical snapshots are neither page-walk evidence nor proof of any instruction in this later interval.'],
 limitations='Static decoded bytes and host marker tests; no physical cache/interrupt/SMBus or paging qualification. Data regions are excluded from linear decoding.')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS',len(rows),'bounded code intervals')
