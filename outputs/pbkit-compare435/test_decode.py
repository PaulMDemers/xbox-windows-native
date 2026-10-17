"""Synthetic transport negatives; no hardware result implied."""
import json,struct
from pathlib import Path
from decode import decode,expected,paired,terminal
K=Path(__file__).resolve().parent
out=K/'host001.json';assert not out.exists()
negative=0
def reject(fn):
    global negative
    try: fn()
    except ValueError: negative+=1
    else: raise AssertionError('Mutation accepted')

models=[]
for phase in range(4):
    r=[0]*128;r[:6]=[0x435c0de,1,phase,1920,1080,7680]
    r[6:11]=[0x2000000,0x2000000,8294400,0x82000000,13000]
    r[13:16]=[60,32,4];r[20:22]=[23,29];r[23]=int(phase>=2)
    if phase>=2:r[24:28]=[1920,1080,7680,0x1000000]
    r[44]=0xc0;r[49]=0x60;r[64]=0x2000000;r[68]=1079
    data=struct.pack('<128I',*r)+expected(phase)
    models.append(decode(data,phase))
    for index in [0,1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,18,20,21,23,28,29,31,55,64,68,93,127]:
        b=bytearray(data);struct.pack_into('<I',b,index*4,0xffffffff)
        reject(lambda:decode(b,phase))
    for index in [512,512+4*319,512+4*320,512+4*640,512+4*960,len(data)-1]:
        b=bytearray(data);b[index]^=1;reject(lambda:decode(b,phase))
    reject(lambda:decode(data[:-1],phase));reject(lambda:decode(data+b'\0',phase))
paired(models)
models[2]['physical']+=4096;reject(lambda:paired(models));models[2]['physical']-=4096
records=[]
for event,count,init in zip([99,10,11,20,21,12,13,100],[0,1,2,2,2,3,4,4],[0,0,0,0,0,1,1,0]):
    records.append([0x435c0de,1,event,0,count,init,13000,0x82000000,0x2000000,8294400,0x2000000,3,1,0,0,0])
j=b''.join(struct.pack('<16I',*r) for r in records);terminal(j)
for rec in range(8):
    for index in [0,1,2,3,4,5,13]:
        b=bytearray(j);struct.pack_into('<I',b,rec*64+index*4,0xffffffff);reject(lambda:terminal(b))
reject(lambda:terminal(j[:-1]));reject(lambda:terminal(j+b'\0'))
out.write_text(json.dumps(dict(passed=True,negative_cases=negative,synthetic=True,
    independent_pattern_pixels=4*524288,physical_access=False),indent=2)+'\n')
print(out.read_text())
