"""Closed actual capture analysis, independent pixels and actual negative controls."""
import hashlib,json,struct
from pathlib import Path
from decode import decode,terminal,paired
K=Path(__file__).resolve().parent;P=Path('C:/xwn435/physical001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'analysis001.json';assert not out.exists()
c=json.loads((K/'physical001-collection.json').read_text());assert c['completed']
for name,r in c['files'].items():assert sha(P/name)==r['sha256']
term=terminal((P/'result.dat').read_bytes());modes=[];negative=0
for phase in range(4):
    data=(P/f'phase-{phase}.dat').read_bytes();modes.append(decode(data,phase))
    for index in [0,2,5,6,7,9,11,16,20,23,28,44,49,64,68,93]:
        b=bytearray(data);struct.pack_into('<I',b,index*4,0xffffffff)
        try:decode(b,phase)
        except ValueError:negative+=1
        else:raise AssertionError('Actual header mutation accepted')
    for pixel in [0,319,320,639,640,959,960,1023,1024,524287]:
        b=bytearray(data);b[512+pixel*4]^=1
        try:decode(b,phase)
        except ValueError:negative+=1
        else:raise AssertionError('Actual pixel mutation accepted')
changes=paired(modes)
out.write_text(json.dumps(dict(passed=True,journal=term,phases=modes,register_changes=changes,
    independent_pixels=2097152,actual_negative_cases=negative,signal_qualified=False,
    visual_result='Separate user observation; not inferred from CPU capture'),indent=2)+'\n')
print(dict(independent_pixels=2097152,actual_negative_cases=negative,register_changes=changes))
