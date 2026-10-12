"""Independent checkpoint rules. No acceptance derived from observed pixels."""
import struct,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'owned-texture271'))
import oracle

def disjoint(ranges):
    for i,(name,start,size) in enumerate(ranges):
        assert 0<size and 0<=start<0x4000000 and start+size<=0x4000000,(name,'bounds')
        for other,a,n in ranges[:i]:assert start+size<=a or a+n<=start,(name,other,'overlap')

def state(data,phase,previous):
    assert len(data)==1612
    h=struct.unpack_from('<43I',data)
    assert h[:3]==(0x58323731,271,1612)
    assert phase in (11,22,33,255) and h[3]==previous
    assert h[5]==(0 if previous==0 else 0x271c0de)
    if phase==255:return dict(error=h[4],passed=False,terminal=True)
    assert h[4]==0 and h[22:27]==(16,8,64,4096,256)
    assert h[34]==(2 if phase==11 else 3)
    assert all(x<=10000 for x in h[35:35+h[34]])
    assert h[39]==0 and h[41]==0
    assert data[172:892]==oracle.framebuffer(),'Initial framebuffer mismatch'
    if phase!=11:oracle.validate_record(data)
    return dict(passed=True,terminal=phase==33,exact_pixel_bytes=720 if phase==11 else 1440)

def translate(read,cr3,cr4,va):
    assert not cr4&0x20,'PAE unsupported'
    def word(a):
        assert 0<=a<=0x4000000-4
        return struct.unpack('<I',read(a,4))[0]
    at=(cr3&0xfffff000)+(va>>22)*4;pde=word(at);assert pde&1
    r=dict(pde_address=at,pde=pde)
    if pde&128:
        assert cr4&16
        r['large']=True;return (pde&0xffc00000)+(va&0x3fffff),r
    at=(pde&0xfffff000)+((va>>12)&1023)*4;pte=word(at);assert pte&1
    r.update(pte_address=at,pte=pte,large=False)
    return (pte&0xfffff000)+(va&4095),r
