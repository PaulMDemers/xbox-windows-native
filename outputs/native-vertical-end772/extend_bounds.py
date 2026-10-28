"""Retain failed payload001; enlarge only the admitted payload extent within its reservation."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K/'payload_build.py').read_text().replace('payload001','payload002').replace('9916','12800')
p=K/'payload_build002.py';assert not p.exists();p.write_text(s,newline='\n')
for n in ['host_build005.py','model.py']:
 p=K/n;p.write_text(p.read_text().replace('payload001','payload002'),newline='\n')
for n in ['main.c','page002.c','page_tool003.c','page_review003.py','bridge.S']:
 p=K/n;s=p.read_text().replace('9916','12800').replace('9915','12799')
 if n=='page_review003.py':s=s.replace('0x206000','0x207000')
 p.write_text(s,newline='\n')
assert 0x1000+12800==0x4200<0x4800
assert 0x5100+256*4==0x5500<0x6000
print('Updated bounded extent; original payload001 failure retained')
