"""Disk encoding and actual loaded representation must each match their contract."""
import hashlib,json,struct
from pathlib import Path
from trampoline import verify_stub
K=Path(__file__).resolve().parent;out=K/'host002.json';assert not out.exists()
x=Path('C:/xwn520/build001/default.xbe').read_bytes()
t=json.loads((K.parent/'entry-observer517/emu001/trace.json').read_text())
items={r['label']:r for r in t['reads']}
def raw(n):
    r=items[n];b=Path(r['private_file']).read_bytes();assert hashlib.sha256(b).hexdigest()==r['sha256'];return b
h=bytearray(raw('trampoline-loaded-header'));s=raw('trampoline-five-bytes')
for offset,length in [(0x10c,4),(0x350,4),(0x358,4),(0x36c,20)]:h[offset:offset+length]=x[offset:offset+length]
h=bytes(h)
verify_stub(h,s,x)
cases=[]
# Disk bytes are never accepted as loaded bytes, or vice versa.
cases.append((x[:4096],s,x))
q=bytearray(x);q[296:300]=h[296:300];cases.append((h,s,q))
for index in range(32):
    for kind in ['loaded','disk']:
        q=bytearray(h if kind=='loaded' else x);q[296+index//8]^=1<<(index%8)
        cases.append((q,s,x) if kind=='loaded' else (h,s,q))
for index in range(40):
    q=bytearray(s);q[index//8]^=1<<(index%8);cases.append((h,q,x))
for item in range(3):
    for amount in [-1,1]:
        a=[h,s,x];a[item]=a[item][:-1] if amount<0 else a[item]+b'\0';cases.append(tuple(a))
for offset in (0x10c,0x350,0x358):
    for bit in range(32):
        for side in ('loaded','disk'):
            q=bytearray(h if side=='loaded' else x);q[offset+bit//8]^=1<<(bit%8)
            cases.append((q,s,x) if side=='loaded' else (h,s,q))
for case in cases:
    try:verify_stub(*case)
    except ValueError:pass
    else:raise AssertionError('negative accepted')
r=dict(passed=True,modeled520_header_from_retained517_and_actual520_stub_positive=True,negative_cases=len(cases),
       retained_capture_sha256={n:r['sha256'] for n,r in items.items()},
       CPU_and_loaded_state_execution_not_replayed=True,physical_access=False,
       sources={n:hashlib.sha256((K/n).read_bytes()).hexdigest() for n in ['trampoline.py','host002.py']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
