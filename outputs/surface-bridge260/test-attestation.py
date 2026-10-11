"""Exercise actual page-walk/handle decoders against independent synthetic tables."""
import hashlib,json,struct
from pathlib import Path
from attest import translate32,handle_entry
k=Path(__file__).resolve().parent;dest=k/'attestation-review001.json';assert not dest.exists()
memory={};reads=[];checks=0
def put(a,n):
 for i,v in enumerate(struct.pack('<I',n)):memory[a+i]=v
def read(a,n):
 reads.append((a,n));return bytes(memory[a+i] for i in range(n))
def yes(va,expected,cr4=0):
 global checks
 got,walk=translate32(read,0x1000,cr4,va,(0x200000,0x204000));assert got==expected;checks+=1;return walk
def no(fn):
 global checks
 try:fn()
 except (AssertionError,KeyError):checks+=1
 else:raise AssertionError('Negative control accepted')
for va,pa in [(0x81234000,0x200000),(0x81235abc,0x201abc),(0x81236000,0x202000),(0x81237fff,0x203fff)]:
 put(0x1000+4*(va>>22),0x3003);put(0x3000+4*((va>>12)&1023),(pa&~4095)|3)
 yes(va,pa)
assert all(a<0x200000 or a>=0x204000 for a,n in reads)
va=0x80012345;put(0x1000+4*(va>>22),0x400083);yes(va,0x412345,0x10)
no(lambda:yes(va,0x412345));no(lambda:yes(va,0x412345,0x30))
put(0x1000+4*(va>>22),0);no(lambda:yes(va,0))
put(0x1000+4*(va>>22),0x200003);n=len(reads);no(lambda:yes(va,0));assert len(reads)==n+1
put(0x1000+4*(va>>22),0x3003);put(0x3000+4*((va>>12)&1023),0);no(lambda:yes(va,0))
no(lambda:translate32(read,0x1000,0,-1,(0x200000,0x204000)))
no(lambda:translate32(read,0x1000,0,2**32,(0x200000,0x204000)))
off=lambda t,n:8 if n=='Table' else 24
table=0x82000000;top=0x82001000;middle=0x82002000;leaf=0x82003000
put(table+8,top)
for handle in [4,1020,1024,0x3fffc,0x40000,0x3fffffc]:
 put(top+((handle>>18)&255)*4,middle);put(middle+((handle>>10)&255)*4,leaf)
 entry=leaf+((handle>>2)&255)*8;put(entry,0x02345673);put(entry+4,0x12019f)
 body,row=handle_entry(read,table,handle,off);assert body==0x82345688 and row['entry']==entry and row['access']==0x12019f;checks+=1
for handle in [0,1,5,0x4000000,-4]:no(lambda:handle_entry(read,table,handle,off))
put(table+8,top|1);no(lambda:handle_entry(read,table,4,off))
r=dict(passed=True,checks=checks,guest_observed=False,physical_access=False,
 inputs={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['attest.py','test-attestation.py','attestation-inputs001.json']},
 scope='Actual decoder functions: four contiguous small pages, large page, nonresident/PAE/invalid/arena-table guards; NT5 three-level handles/sign/attribute bits/index boundaries. Does not attest a running guest.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('260 page/handle decoder checks',checks,'PASS; synthetic only')
