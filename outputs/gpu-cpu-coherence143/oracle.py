"""Independent integer oracle for all 16 full color/depth readbacks."""
import array,re,sys
W,H=640,480
def expected(epoch,depth,stage):
    assert epoch in [0,1] and depth in [0,1] and stage in range(4)
    values=[0x345678a5,0x789abc3c,0xabcdef5a] if depth else [0xa5317ca4,0xc48259ed,0x9274c13b]
    values=[v ^ (epoch*0x01010100) for v in values]
    pixels=array.array('I',[values[2] if stage==3 else values[0]])*(W*H)
    if stage in [1,2]:
        for y in range(5,34):
            for x in range(3,64):pixels[y*W+x]=0x52100000 ^ (epoch<<20) ^ (depth<<19) ^ (16<<12) ^ (y<<6) ^ x
    if stage==2:
        row=array.array('I',[values[1]])*97
        for y in range(13,66):pixels[y*W+19:y*W+116]=row
    if sys.byteorder!='little':pixels.byteswap()
    return pixels.tobytes()

def validate_log(data):
    lines=data.decode('ascii').splitlines();at=0;surfaces=[]
    def take(pattern):
        nonlocal at
        assert at<len(lines),'Incomplete log'
        m=re.fullmatch(pattern,lines[at]);assert m,(at,lines[at],pattern)
        at+=1;return m
    take(r'BEGIN 143 2 2 4 640 480 17')
    for epoch in range(2):
        take(fr'INIT_BEGIN {epoch}');take(fr'INIT_RETURN {epoch} 0')
        for depth in range(2):
            m=take(fr'SURFACE {epoch} {depth} ([0-9a-f]{{8}}) (\d+)')
            base,pitch=int(m[1],16),int(m[2]);assert 0<base<64*1024**2 and pitch==2560
            assert base+pitch*H<=64*1024**2
            surfaces.append(dict(epoch=epoch,depth=bool(depth),base=base,pitch=pitch))
            for stage in range(4):take(fr'CAPTURE {epoch} {depth} {stage} {base:08x} {pitch} 1228800')
        take(fr'KILL_BEGIN {epoch}');take(fr'KILL_RETURN {epoch}')
    take(r'COMPLETE 16 120292 0');take(r'NORMAL_REBOOT_REQUEST');assert at==len(lines)
    return surfaces

def compare(data,reference):
    if data is None:return dict(matched=False,reason='missing')
    if len(data)!=len(reference):return dict(matched=False,reason='length',actual=len(data),expected=len(reference))
    mismatches=[i for i,(a,b) in enumerate(zip(data,reference)) if a!=b]
    return dict(matched=not mismatches,different_bytes=len(mismatches),first_difference=mismatches[0] if mismatches else None)
