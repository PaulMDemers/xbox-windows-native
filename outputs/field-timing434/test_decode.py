"""Synthetic transport/clock negatives; not hardware raster or pixel validation."""
import json, struct
from pathlib import Path
from decode import decode,terminal,CR,MM
def fixture(stage):
    w,h=(1920,1080) if stage==1 else (1280,720)
    a=[0]*128
    a[:11]=[0x434c0de,1,stage,w,h,w*4,0x1000000,0x1000000,0x900000,1000000,0]
    a[13:22]=[60,32,4,7,7,0x202,0x202,len(CR),len(MM)]
    a[26:28]=[4034,1];a[64]=a[6]
    b=a.copy();b[11]=2000;b[22]=100;b[24]=200100;b[30]=200
    samples=b''.join(struct.pack('<QIQI',100+i*100,(i*3)%563,101+i*100,i) for i in range(2000))
    return struct.pack('<128I',*a)+struct.pack('<128I',*b)+samples
def main():
    k=Path(__file__).resolve().parent;out=k/'host002.json';assert not out.exists()
    good=fixture(1);positive=[decode(fixture(i),i) for i in range(3)]
    mutations=[]
    for header in [0,512]:
        for word in list(range(9))+[10,12,13,14,15,17,19,20,21,28,29,31,55,63,93,127]:
            q=bytearray(good);at=header+word*4
            old=struct.unpack_from('<I',q,at)[0]
            struct.pack_into('<I',q,at,old^(0x200 if word==19 else 1))
            mutations.append(bytes(q))
    for word,value in [(11,32768),(11,0),(22,200101),(24,199999),(30,1000)]:
        q=bytearray(good);struct.pack_into('<I',q,512+word*4,value);mutations.append(bytes(q))
    for offset,value in [(1024,99),(1024+12,98),(1024+20,1),(1024+24,99),(1024+1999*24+12,200101)]:
        q=bytearray(good);struct.pack_into('<I',q,offset,value);mutations.append(bytes(q))
    mutations += [good[:-1],good+b'\0',good[:1000]]
    for q in mutations:
        try:decode(q,1)
        except ValueError:pass
        else:raise AssertionError('accepted invalid transport')
    tr=struct.pack('<16I',0x434c0de,1,99,0,0,0,0,0,0x434c0de,1,100,0,3,0,0,0)
    terminal(tr)
    for i in range(16):
        q=bytearray(tr);q[i*4]^=1
        try:terminal(q)
        except ValueError:pass
        else:raise AssertionError('accepted invalid terminal')
    # Constant and arbitrary high bits remain observations, never guessed parity.
    q=bytearray(good)
    for i in range(2000):struct.pack_into('<I',q,1024+i*24+8,0x80000000)
    assert decode(q,1)['raw_unique']==1 and not decode(q,1)['field_parity_proved']
    r=dict(passed=True,synthetic_positive_cases=4,negative_cases=len(mutations)+16,
           native_build_or_launch=False,field_parity_proved=False)
    out.write_text(json.dumps(r,indent=2)+'\n');print(r)
if __name__=='__main__':main()
