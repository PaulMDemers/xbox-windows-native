# SPDX-License-Identifier: MIT
"""Independent exact extent/capture join on the completed524 runtime."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;OUT=K/'extent-review001.json';assert not OUT.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
t=json.loads((K/'emu001/trace.json').read_bytes());assert t['passed']
x=Path('C:/xwn520/build001/default.xbe').read_bytes();assert len(x)==544096 and sha(x)=='73b3623af2694d3c803f70f49fc9c8c072df54a7010d3238358cf6576589ca13'
rows={r['label']:r for r in t['reads']}
def raw(label):
    r=rows[label];b=Path(r['private_file']).read_bytes();assert len(b)==r['bytes'] and sha(b)==r['sha256'];return b

def verify(h):
    assert len(h)==4096 and h[:4]==b'XBEH'
    assert struct.unpack_from('<I',h,0x104)[0]==0x10000
    assert struct.unpack_from('<I',h,0x10c)[0]==544096
    assert struct.unpack_from('<I',h,0x34c)[0]==0x11000
    assert struct.unpack_from('<I',h,0x350)[0]==540000
    assert struct.unpack_from('<I',h,0x354)[0]==4096
    assert struct.unpack_from('<I',h,0x358)[0]==540000
    assert h[0x36c:0x380]==x[0x36c:0x380]
    assert 0x11000+540000==0x10000+544096==0x94d60
    return True
headers=[raw('trampoline-loaded-header'),raw('loaded-xbe-header')]
for h in headers:assert verify(h)
assert raw('entry-code')==x[0x84877:0x84877+929]
assert raw('entry-data')==x[0x84c20:0x84d60]
assert raw('path')==b'\\Device\\Harddisk0\\Partition1\\Applications\\XWNBoot520a\\entry.bin\0'
rejected=0
for h in headers:
    for off in (0x10c,0x350,0x358):
        for bit in range(32):
            q=bytearray(h);q[off+bit//8]^=1<<(bit%8)
            try:verify(q)
            except AssertionError:rejected+=1
            else:raise AssertionError('bad actual extent accepted')
audit=json.loads((K/'emu001/audit.json').read_bytes());assert audit['candidate_exact'] and audit['receipts']['entry.bin']['memory_exact']
r=dict(passed=True,actual_loaded_headers=2,image_bytes=544096,section_bytes=540000,exclusive_image_end=0x94d60,rounded_page_end=0x95000,actual_initial_code_bytes=929,actual_initial_data_bytes=320,extent_mutations_rejected=rejected,actual_cold_candidate_exact=True,full_address_space_or_physical_boot_cause_proved=False,physical_access=False,source_sha256=sha(Path(__file__).read_bytes()),capture_sha256={n:rows[n]['sha256'] for n in ['trampoline-loaded-header','loaded-xbe-header','entry-code','entry-data','path']})
OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
