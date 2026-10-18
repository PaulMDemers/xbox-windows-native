"""Independent retained-byte and two-state check; no live reads or reuse."""
import copy, hashlib, json, struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'trampoline-review001.json';assert not out.exists()
t=json.loads((K/'emu001/trace.json').read_text());reads={r['label']:r for r in t['reads']}
def raw(label):
    r=reads[label];b=Path(r['private_file']).read_bytes()
    assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256']
    return b
lo=t['checkpoints'][0];hi=t['checkpoints'][1]
header=raw('trampoline-loaded-header');stub=raw('trampoline-five-bytes')
fields=('EAX','EBX','ECX','EDX','ESI','EDI','EBP','ESP','EFL','CR0','CR3','CR4')
def verify(a,b,h,s):
    assert a['label']=='trampoline-entry' and b['label']=='early-entry'
    assert a['registers']['EIP']==0x11100 and b['registers']['EIP']==0x94aff
    assert len(h)==4096 and struct.unpack_from('<I',h,296)[0]==0xa8fd46ab
    assert s==bytes.fromhex('e9fa390800')
    for n in fields:assert type(a['registers'][n]) is int and a['registers'][n]==b['registers'][n]
    return True
assert verify(lo,hi,header,stub)
count=0
for side in [0,1]:
    for name in fields+('EIP',):
        a,b=copy.deepcopy(lo),copy.deepcopy(hi);[a,b][side]['registers'][name]^=1
        try:verify(a,b,header,stub)
        except AssertionError:count+=1
        else:raise AssertionError((side,name))
for i in range(5):
    s=bytearray(stub);s[i]^=1
    try:verify(lo,hi,header,s)
    except AssertionError:count+=1
    else:raise AssertionError(i)
for i in range(296,300):
    h=bytearray(header);h[i]^=1
    try:verify(lo,hi,h,stub)
    except AssertionError:count+=1
    else:raise AssertionError(i)
assert not any(r['registers']['EIP']==0x11105 for r in t['checkpoints'])
assert any(b['command']=='Z1,11105,1' and b['reply']=='OK' for b in t['breakpoints'])
assert any(b['command']=='z1,11105,1' and b['reply']=='OK' for b in t['breakpoints'])
assert t['passed'] and t['remaining_breakpoints']==[] and t['physical_mode_restored']
assert t['trampoline']['before']==lo['registers'] and t['trampoline']['after']==hi['registers']
r=dict(passed=True,actual_state_and_byte_mutations_rejected=count,entry=0x11100,target=0x94aff,
       preparation_guard=0x11105,compared_fields=list(fields),physical_access=False)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
