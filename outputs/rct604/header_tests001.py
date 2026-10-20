"""Independent Python decoder positive/rejection controls before guest use."""
import json
from pathlib import Path
from dib_oracle import decode_header
K=Path(__file__).resolve().parent;out=K/'header-tests001.json';assert not out.exists()
base=[40,8,0xfffffff8,0x200001,0,0,0,0,0,0]
cases=[('topdown',0x1000,base,0,(0,32,256)),('bottomup',0x1000,[40,8,8,*base[3:]],0,(0,32,256)),('null',0,[],1,(1,0,0)),('wrap',0xffffffff,[],2,(2,0,0)),('unreadable',0x1000,[],3,(3,0,0)),('truncated',0x1000,[40],3,(3,0,0)),('unsupported',0x1000,[124],4,(4,0,0))]
for name,index,value,status in [('width',1,0,5),('height_min',2,0x80000000,5),('planes',3,0x200002,6),('bpp',3,0x30001,7),('compression',4,1,8),('dimension_limit',1,16385,9),('sizeimage',5,1,10),('palette',8,257,11)]:
 raw=base.copy();raw[index]=value;cases.append((name,0x1000,raw,status,(status,32,256) if status in [10,11] else (status,0,0)))
for name,addr,raw,status,want in cases:assert decode_header(addr,raw,status)==want,name
rejected=[]
for name,addr,raw,status in [('false_read_success',0x1000,[],0),('missing_body',0x1000,[40],0),('extra_words',0x1000,base+[0],0),('null_with_words',0,base,0),('address_overflow',2**32,[],2),('word_overflow',0x1000,[40,2**32,*base[2:]],0)]:
 try:decode_header(addr,raw,status)
 except AssertionError:rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,positive=[c[0] for c in cases],rejected=rejected,scope='Python raw-record decoder controls; actual NT5 transport still required.'),indent=2)+'\n')
print('604 Python header decoder cases passed')
