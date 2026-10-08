"""Independent rectangular Morton addressing and entire-arena byte oracle."""
import re
SIZE=32768
def index(x,y,width,height):
    assert 0<=x<width and 0<=y<height
    # Build address bit positions from dimension lengths, independent of guest loop.
    xbits=width.bit_length()-1;ybits=height.bit_length()-1
    order=[]
    for bit in range(max(xbits,ybits)):
        if bit<xbits:order.append((x,bit))
        if bit<ybits:order.append((y,bit))
    return sum(((value>>bit)&1)<<pos for pos,(value,bit) in enumerate(order))
def expected(shape,depth,stage):
    assert shape in [0,1] and depth in [0,1] and stage in range(3)
    w,h=(32,64) if shape else (64,32);bpp=2 if depth else 4
    data=bytearray([0xa5])*SIZE
    def put(x,y,value):
        at=index(x,y,w,h)*bpp;data[at:at+bpp]=value.to_bytes(bpp,'little')
    for y in range(6,18):
        for x in range(8,24):put(x,y,0 if depth else 0xffff00ff)
    if stage>=1:
        put(3,5,0x4321 if depth else 0xff123456);put(12,9,0x9876 if depth else 0xff765432)
    if stage>=2:
        for y in range(11,23):
            for x in range(17,29):put(x,y,16384 if depth else 0xff00ffff)
    return bytes(data)
def compare(data,ref):
    if data is None:return dict(matched=False,reason='missing')
    if len(data)!=len(ref):return dict(matched=False,reason='length',actual=len(data),expected=len(ref))
    errors=[i for i,(a,b) in enumerate(zip(data,ref)) if a!=b]
    return dict(matched=not errors,different_bytes=len(errors),first_difference=errors[0] if errors else None)
def validate_log(data):
    lines=data.decode('ascii').splitlines();at=0;surfaces=[]
    def take(pattern):
        nonlocal at
        assert at<len(lines);m=re.fullmatch(pattern,lines[at]);assert m,(at,lines[at],pattern);at+=1;return m
    take('BEGIN 154 2 2 3 32768');take('INIT_RETURN 0')
    for d in range(2):
        m=take(fr'ARENA {d} ([0-9a-f]{{8}}) 32768');base=int(m[1],16);assert 0<base<64*1024**2-SIZE
        surfaces.append(dict(depth=bool(d),base=base,bpp=2 if d else 4))
    for q in range(2):
        take(f'SHAPE {q} '+('32 64' if q else '64 32'));take(f'DEPTH_MODE {q} 00100001');take(f'DRAW_IDLE {q} 0')
        for d in range(2):take(f'CAPTURE {q} {d} 0 32768')
        take(f'CPU_PATCH {q} 4')
        for d in range(2):take(f'CAPTURE {q} {d} 1 32768')
        take(f'DRAW_IDLE {q} 1')
        for d in range(2):take(f'CAPTURE {q} {d} 2 32768')
    take('KILL_RETURN');take('COMPLETE 12 8 0');take('NORMAL_REBOOT_REQUEST');assert at==len(lines)
    return surfaces
