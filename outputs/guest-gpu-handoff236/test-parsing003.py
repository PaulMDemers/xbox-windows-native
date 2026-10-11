"""Exact owned entry mapping and adversarial post-write/journal discrimination."""
import copy,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'parsing-test003.json';assert not dest.exists()
sys.path.insert(0,str(ws/'work/python-packages'));import capstone
from parsing import xbe,span,after_write_instruction,journal_ack
checks=0
def check(ok):
 global checks
 assert ok;checks+=1
def reject(fn):
 global checks
 try:fn()
 except AssertionError:checks+=1;return
 raise AssertionError('Malformed proof accepted')
inventory=json.loads((k/'inventory001.json').read_text())
for name,key in [('dashboard','dashboard'),('xromwell','launcher')]:
 raw=(k/'artifacts/inputs'/f'{name}.xbe').read_bytes();layout=xbe(raw);check(layout==inventory[key])
 entry=layout['entry'];check(len(span(raw,layout,entry,32))==32)
 reject(lambda:xbe(raw[:0x177]));reject(lambda:span(raw,layout,entry,4097));reject(lambda:span(raw,layout,0xffffffff,32))
 for offset,value in [(0x104,0),(0x108,len(raw)+1),(0x10c,0),(0x11c,0),(0x11c,33),(0x120,0xffffffff),(0x128,0)]:
  damaged=bytearray(raw);struct.pack_into('<I',damaged,offset,value);reject(lambda:xbe(damaged))
 # A span crossing into zero-fill is not a resident-byte ownership proof.
 section=layout['sections'][0];reject(lambda:span(raw,layout,section['address']+section['file_bytes']-1,32))
 overlap=copy.deepcopy(layout);overlap['sections'].append(copy.deepcopy(section));reject(lambda:span(raw,overlap,section['address'],32))
 check(span(raw,layout,entry,32)==raw[section['file_offset']+entry-section['address']:section['file_offset']+entry-section['address']+32])
registers=[0x100000,0xfd400100,0x100000,0,0x30000,0,0,0,0,0]
def decode(hexcode,values=registers):
 raw=bytes.fromhex(hexcode);return after_write_instruction(raw,0x1000,0x1000+len(raw),values,capstone)
for machine in ['8901','8911','a3000140fd','8905000140fd']:
 rows=decode(machine);check(len(rows)==1 and rows[0]['value']==0x100000 and rows[0]['address']==0x1000)
rows=decode('c705000140fd00001000');check(any(r['address']==0x1000 and r['value']==0x100000 for r in rows))
check(len(rows)==1)
# Reject suffix proof through operand/segment/repetition overrides.
for machine in ['8902','8801','668901','648901','f38901','90','0101']:
 check(not decode(machine))
bad=registers.copy();bad[1]=0xfd400104;check(not decode('8901',bad))
index=registers.copy();index[3]=0xfd400000;index[1]=0x40
rows=decode('89048b',index);check(len(rows)==1 and rows[0]['effective_address']==0xfd400100)
check(not after_write_instruction(bytes.fromhex('8901'),0x2000,0x1002,registers,capstone))
header='version=234 state=3 tuple_published=1 total=2 count=2 capacity=256 overwritten=0 '
current=[0,1,9,0,0,0,0,0,0,0,0]+[0]*10
before=[1,2,4,0x100000,0x100000,0x100000,1,0x100,0x7a080101,2,1]+[0]*10
after=[2,3,5,0x100000,0,0x100000,1,0x100,0x7a080101,0,1]+[0]*10
def reply(rows=[current,before,after]):return header+' '.join('row='+','.join(map(str,r)) for r in rows)
check(journal_ack(reply(),0x100000)['ack_after']==after)
for field,value in [(0,3),(2,4),(3,0),(4,0x100000),(9,2),(10,0)]:
 rows=copy.deepcopy([current,before,after]);rows[2][field]=value;reject(lambda:journal_ack(reply(rows),0x100000))
reject(lambda:journal_ack(reply(),0x200000))
reject(lambda:journal_ack(reply().replace('state=3','state=5'),0x100000))
reject(lambda:journal_ack(reply().replace('overwritten=0','overwritten=1'),0x100000))
reject(lambda:journal_ack(reply([current,before]),0x100000))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(dict(passed=True,checks=checks,capstone_version=capstone.__version__,source_sha256=sha(k/'parsing.py'),test_sha256=sha(Path(__file__)),physical_access=False,guest_launch=False),indent=2)+'\n')
print('236 parser checks',checks)
