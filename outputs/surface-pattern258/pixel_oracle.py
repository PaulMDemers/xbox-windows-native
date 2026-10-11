"""Independent host contract for a future isolated BGRA8 surface; no guest execution."""
import hashlib,json
from pathlib import Path
SIZE=16384
OFFSET=4096
WIDTH,HEIGHT,PITCH=13,11,64
def cpu(seed):
    assert seed in [0,1,2]
    return bytes(((37*i+19*(i//16)+7*(i//256))^(83*seed))&255 for i in range(SIZE))
def pixel(x,y):
    assert 0<=x<WIDTH and 0<=y<HEIGHT
    # Bytes B,G,R,A; rows use GL texture coordinates, no display-origin assumption.
    return bytes(((17*x+29*y+3)&255,(71*x+11*y+19)&255,(5*x+97*y+101)&255,255))
def texture():return b''.join(pixel(x,y) for y in range(HEIGHT) for x in range(WIDTH))
def expected():
    out=bytearray(cpu(0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            p=OFFSET+y*PITCH+4*x;out[p:p+4]=pixel(x,y)
    return bytes(out)
def compare(actual,want):
    assert len(want)==SIZE
    if len(actual)!=SIZE:return dict(passed=False,wrong_length=True)
    bad=[i for i in range(SIZE) if actual[i]!=want[i]]
    return dict(passed=not bad,mismatches=len(bad),first_mismatch=bad[0] if bad else None)
if __name__=='__main__':
    k=Path(__file__).resolve().parent;dest=k/'pixel-oracle-review.json';assert not dest.exists()
    want=expected();upload=texture();assert len(upload)==WIDTH*HEIGHT*4 and compare(want,want)['passed']
    changed={OFFSET+y*PITCH+x for y in range(HEIGHT) for x in range(WIDTH*4)}
    assert all(want[i]==cpu(0)[i] for i in range(SIZE) if i not in changed)
    assert len(changed)==572 and len(set(pixel(x,y) for y in range(HEIGHT) for x in range(WIDTH)))==143
    cases={}
    for label,raw in [('stale_cpu',cpu(0)),('stale_gpu_after_cpu_store',want)]:
        cases[label]=compare(raw,want if label=='stale_cpu' else cpu(1));assert not cases[label]['passed']
    for label,pos in [('prefix_guard',OFFSET-1),('row_padding',OFFSET+WIDTH*4),('suffix_guard',OFFSET+PITCH*HEIGHT),('wrong_pixel',OFFSET+17)]:
        raw=bytearray(want);raw[pos]^=1;cases[label]=compare(raw,want);assert cases[label]['mismatches']==1
    for label in ['wrong_stride','flipped_rows','red_blue_swap']:
        raw=bytearray(cpu(0))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pos=OFFSET+y*(WIDTH*4 if label=='wrong_stride' else PITCH)+x*4
                value=pixel(x,HEIGHT-1-y if label=='flipped_rows' else y)
                if label=='red_blue_swap':value=bytes((value[2],value[1],value[0],value[3]))
                raw[pos:pos+4]=value
        cases[label]=compare(raw,want);assert not cases[label]['passed']
    r=dict(passed=True,guest_executed=False,gl_executed=False,physical_access=False,
           pixel_preservation_proved=False,allocation_bytes=SIZE,surface_offset=OFFSET,width=WIDTH,height=HEIGHT,pitch=PITCH,
           exact_pixel_bytes=len(changed),guard_and_padding_bytes=SIZE-len(changed),
           texture_sha256=hashlib.sha256(upload).hexdigest(),expected_read_sha256=hashlib.sha256(want).hexdigest(),
           expected_post_cpu_store_sha256=hashlib.sha256(cpu(1)).hexdigest(),negative_controls=cases)
    dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
