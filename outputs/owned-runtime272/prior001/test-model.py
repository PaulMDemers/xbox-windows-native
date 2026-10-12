"""Synthetic negatives for phase ABI, pixels and address translation."""
import json,struct
from pathlib import Path
from model import state,disjoint,translate,oracle
k=Path(__file__).resolve().parent;dest=k/'model-tests001.json';assert not dest.exists()
h=[0]*43;h[:6]=[0x58323731,271,1612,0,0,0]
for u in range(4):h[6+u]=0x81000000+u*4096;h[10+u]=0x1000000+u*4096;h[14+u]=h[6+u]+256;h[18+u]=h[10+u]+256
h[22:27]=[16,8,64,4096,256];h[27:35]=[0x82000000,0x2000000,2560,480,0x81800000,384,0x1800000,2]
data=struct.pack('<43I',*h)+oracle.framebuffer()+bytes(720)
assert state(data,11,0)['passed'];rejections=0
for offset in [0,4,8,12,16,20,88,136,156,164]+list(range(172,892)):
    bad=bytearray(data);bad[offset]^=1
    try:state(bytes(bad),11,0)
    except AssertionError:rejections+=1
    else:raise AssertionError(('Accepted mutation',offset))
h[3]=11;h[5]=0x271c0de;h[34]=3
assert state(struct.pack('<43I',*h)+oracle.framebuffer()*2,22,11)['passed']
for ranges in [[('a',0,4096),('b',4095,2)],[('a',0x4000000,1)],[('a',1,0)]]:
    try:disjoint(ranges)
    except AssertionError:rejections+=1
    else:raise AssertionError('Bad interval accepted')
disjoint([('a',0,4096),('b',4096,4096)])
words={0x1000+512*4:0x2001,0x2000+3*4:0x7001}
read=lambda a,n:struct.pack('<I',words[a])
assert translate(read,0x1000,0,0x80003004)[0]==0x7004
words[0x1000+512*4]=0x800081
assert translate(read,0x1000,16,0x80003004)[0]==0x803004
words[0x1000+512*4]=0
try:translate(read,0x1000,0,0x80003004)
except AssertionError:rejections+=1
else:raise AssertionError('Nonpresent page accepted')
dest.write_text(json.dumps(dict(passed=True,rejected_mutations=rejections,scope='Synthetic model only; no live guest qualification'),indent=2)+'\n')
print(dest.read_text())
