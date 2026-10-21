"""Synthetic receipt corruption tests; never count as a Windows result."""
import hashlib,json
from pathlib import Path
from result_parser import analyze
K=Path(__file__).resolve().parent
pairs=[('case',639),('begin.tick',1000),('mode.query',1),('mode.width',720),('mode.height',480),('mode.bpp',32),('mode.frequency',60),('mode.expected',1),('screen.width',720),('screen.height',480),('window.class',1),('window.created',1),('dd.create',0),('dd.cooperative',0),('dd.primary',0),('dd.describe',0),('primary.flags',0x100f),('primary.width',720),('primary.height',480),('primary.pitch',2880),('primary.bpp',32),('primary.geometry',1),('miniport.enumerate',1),('miniport.open',0),('miniport.error',5),('draw.client',1)]
for i in range(3):
 pairs.append(('draw.upload',1))
 if i:pairs.append(('draw.overlap',1))
 pairs.extend([('draw.flush',1),('draw.readback',1),('readback.flush',1),('pass%d.mismatches'%i,0)])
pairs.extend([('input.seed_created',1),('input.seed_written',1),('input.deadline_ms',300000),('input1.started',1),('input1.closed',1),('input1.exit_query',1),('input1.exit_code',0),('input1.readback',1),('input1.bytes',7),('input1.matches',1),('input2.started',1),('input2.closed',1),('input2.exit_query',1),('input2.exit_code',0),('input2.readback',1),('input2.bytes',7),('input2.unchanged',1),('input.complete',1)])
pairs.extend([('failures',0),('complete',1),('end.tick',15000),('restart.lookup',1),('restart.privilege',1),('restart.requesting',1),('restart.accepted',1)])
enc=lambda p:''.join('%s=%d\r\n'%row for row in p).encode()
b=enc(pairs);assert analyze(b)['passed'];negative=0
for i in range(len(pairs)):
 for changed in [pairs[:i]+pairs[i+1:],pairs[:i]+[pairs[i]]+pairs[i:]]:
  assert not analyze(enc(changed))['passed'];negative+=1
 if pairs[i][0] not in ['begin.tick','end.tick','mode.frequency','miniport.error']:
  changed=list(pairs);changed[i]=(pairs[i][0],pairs[i][1]+1);assert not analyze(enc(changed))['passed'];negative+=1
for bad in [None,b'',b[:-1],b+b'extra=1\r\n',b.replace(b'mode.width=720',b'mode.width=-720'),b.replace(b'case=639',b'case=4294967296'),b.replace(b'end.tick=15000',b'end.tick=1')]:
 assert not analyze(bad)['passed'];negative+=1
(K/'parser-tests001.json').write_text(json.dumps(dict(passed=True,scope='synthetic parser tests',negative_cases=negative,parser_sha256=hashlib.sha256((K/'result_parser.py').read_bytes()).hexdigest()),indent=2)+'\n')
print('Parser PASS:',negative,'negative cases')
