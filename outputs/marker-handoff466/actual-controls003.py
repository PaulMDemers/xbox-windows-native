"""Rehash actual captures and reject inconsistent successful-marker records."""
import hashlib,json,struct
from pathlib import Path
from marker_decode import success
from decode import decode
K=Path(__file__).resolve().parent;out=K/'emu003/actual-controls.json';assert not out.exists()
t=json.loads((K/'emu003/trace.json').read_text());assert t['passed'] and not t.get('cleanup_error')
assert t['remaining_breakpoints']==[] and t['physical_mode_restored']
for v in t['reads']:
 data=Path(v['private_file']).read_bytes();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
rows={v['label']:v for v in t['reads']};negative=0
for stage,label in [(1,'first-marker-record'),(2,'second-marker-record')]:
 data=Path(rows[label]['private_file']).read_bytes();success(data,stage);r=list(struct.unpack('<24I',data))
 bads={0:0,1:2,2:95,3:3,4:0,5:5,6:1,7:1,8:0,9:4097,10:0xffffffff,11:0xffffffff,12:0,13:0xffffffff,14:0x800,15:0x20,16:0,17:0,18:2,19:99,20:99,21:0,22:0,23:1}
 for i,bad in bads.items():
  c=r[:];c[i]=bad
  try:success(struct.pack('<24I',*c),stage)
  except ValueError:negative+=1
  else:raise AssertionError(('mutation accepted',stage,i))
 for n in range(96):
  try:success(data[:n],stage)
  except ValueError:negative+=1
  else:raise AssertionError('truncation accepted')
p=Path(rows['primary-memory-report']['private_file']).read_bytes();v=decode(p);words=struct.unpack('<44I',p)
cp={v['label']:v['registers'] for v in t['checkpoints']}
assert cp['before_original_loader_cli']['EIP']==v['loader_physical']
assert cp['before_original_loader_cli']['EFL']==words[28]
assert cp['second_marker_terminal']['EFL']==cp['before_stack_install']['EFL']
out.write_text(json.dumps(dict(passed=True,actual_marker_mutations_rejected=negative,captures_rehashed=len(t['reads']),
    actual_dynamic_loader=v['loader_physical'],full_eflags_preserved_both_boundaries=True,physical_access=False),indent=2)+'\n')
