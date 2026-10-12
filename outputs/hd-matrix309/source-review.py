import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent
raw=Path('D:/xwn307/physical001/kernel307.bin').read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(raw)=='717482bc649804080820f05723fce6cc8b114f6ca95d134c94d9d0ed1895083b'
base=0x80010000
regions=[(0x8001594c,0x80015985,'read transfer setup'),(0x80015985,0x80015a1f,'exported read routine'),(0x80015f2b,0x80015fcd,'completion callback'),(0x80015f90,0x80015fc4,'request status and raw controller data transfer')]
pins=[dict(address=hex(a),bytes=b-a,sha256=sha(raw[a-base:b-base]),meaning=m) for a,b,m in regions]
assert raw[0x15fa2-0x10000:0x15fab-0x10000].hex()=='66ba06c066ed0fb7c0'
idx=list(raw[0x3654:0x3661]);assert idx==[214,46,50,60,62,64,196,198,206,160,158,156,108]
from decode import MATRIX
for stage,profile in enumerate([2,3,1]):
 table=list(raw[0x3654+13*profile:0x3654+13*(profile+1)])
 assert table[-1]==70 and table[:-1]+[40]==MATRIX[stage]
s=(k/'main.c').read_text();expected='static const unsigned char matrix[3][13]={\n'+',\n'.join(' {'+','.join(map(str,p))+'}' for p in MATRIX)+'\n};'
assert expected in s and 'encoder309.value[i]!=matrix[stage-1][i-1]' in s
assert 'HalWriteSMBusValue(' not in s
r=dict(passed=True,read_only_static_analysis=True,kernel_sha256=sha(raw),resident_pins=pins,independent_matrix=MATRIX,completion='On ordinary pending request path status stored, 16-bit portC006 input zero-extended into request+4, caller byte path takes low8 bits. No register-specific mapping in reviewed path.',limitations='ISR entry dispatch and actual bus waveform not captured. This does not explain physical6c0 or establish exact part revision.',old308_qualification=False,new_scope='Thirteen specifically addressed values;6cUNKNOWN; no full encoder readback or Windows mode qualification')
p=k/'source-review001.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print('Static completion pins and matrix source review passed')
