import json,hashlib
from pathlib import Path
from oracle import expected,compare,validate_log
k=Path(__file__).resolve().parent
ref=expected();assert compare(ref)['matched']
mutations=[('missing',None),('short',ref[:-1]),('empty_rectangle',b'\x4a\x32\x15\xff'*(640*480))]
for name,offset in [('inside',(100*640+140)*4),('outside',(5*640+3)*4)]:
 b=bytearray(ref);b[offset]^=1;mutations.append((name,bytes(b)))
for name,b in mutations:assert not compare(b)['matched'],name
log=(k.parent/'gpu-draw-lifetime145/control001/artifacts/result.log').read_bytes()
validate_log(log)
bad=[log.replace(b'BEGIN_IDLE 2',b'BEGIN_IDLE 9'),log.replace(b'CPU_STORE 2 3 5 ff15324a',b'CPU_STORE 2 3 5 00000000'),log.replace(b'COMPLETE 4 3 0',b'COMPLETE 4 3 1'),log+b'EXTRA\r\n']
for b in bad:
 try:validate_log(b)
 except AssertionError:pass
 else:raise AssertionError('Invalid protocol accepted')
p=k/'oracle-tests.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,pixel_failure_gates=[n for n,_ in mutations],protocol_failure_gates=len(bad),oracle_sha256=hashlib.sha256((k/'oracle.py').read_bytes()).hexdigest()),indent=2)+'\n')
print('Independent pixel/protocol failure gates pass')
