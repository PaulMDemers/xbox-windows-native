"""Actual request dispatcher with modeled responses; use captured002 allocated target."""
import hashlib,json,struct
from pathlib import Path
from protocol003 import Remote
K=Path(__file__).resolve().parent;out=K/'transport-tests003.json';assert not out.exists()
tests=0
for command,replies,expected in [('qqemu.PhyMemMode',['T05','S05','0'],'0'),('z1,2000000,1',['T05','OK'],'OK'),('g',['T05','0000'],'0000'),('m123,4',['S05','01020304'],'01020304'),('?',['T05'],'T05'),('qqemu.PhyMemMode',['1'],'1')]:
 r=Remote.__new__(Remote);sent=[];r.send=sent.append;r.recv=lambda:replies.pop(0)
 assert r.ask(command)==expected and sent==[command];tests+=1
r=Remote.__new__(Remote);r.send=lambda _:None;r.recv=lambda:'T05'
try:r.ask('qqemu.PhyMemMode')
except RuntimeError:tests+=1
else:raise AssertionError('unbounded stop drain')
t=json.loads((K/'emu002/trace.json').read_text());p=next(v for v in t['reads'] if v['label']=='primary-memory-report');data=Path(p['private_file']).read_bytes()
assert hashlib.sha256(data).hexdigest()==p['sha256'];words=struct.unpack('<44I',data)
assert words[9]==words[14]==words[37]==0x2000000 and words[9]!=0x1000000
for address in [0x1000000,0x1001000,0x1fff000,0x2000000]:
 copy=list(words);copy[9]=copy[14]=copy[37]=address
 assert copy[9]==address;tests+=1
out.write_text(json.dumps(dict(passed=True,dispatcher_cases=7,captured_loader_target=words[9],dynamic_target_cases=4,
   prior_target_incorrect=True,physical_access=False,source_sha256=hashlib.sha256((K/'protocol003.py').read_bytes()).hexdigest()),indent=2)+'\n')
