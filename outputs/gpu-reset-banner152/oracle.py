"""Whole arena oracle: include overlap, pitch padding and untouched tail bytes."""
import re
SIZE=32768
def expected(depth,stage):
    assert depth in [0,1] and stage in range(3)
    bpp=2 if depth else 4;pitch=128 if depth else 256;other=192 if depth else 320;offset=2048 if depth else 4096
    data=bytearray([0xa5])*SIZE
    def rect(off,p,x,y,w,h,value):
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                i=off+yy*p+xx*bpp;data[i:i+bpp]=value.to_bytes(bpp,'little')
    rect(0,pitch,0,0,64,64,0x3157 if depth else 0xff3157a9)
    rect(offset,other,7,9,17,11,0x6824 if depth else 0xff6824d1)
    if stage>=1:
        for y in range(3,8):
            for x in range(2,7):rect(offset,other,x,y,1,1,(0x9000^(y<<5)^x) if depth else (0x92740000^(y<<8)^x))
    if stage>=2:rect(0,pitch,20,17,11,19,0xbcde if depth else 0xffbcde73)
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
        assert at<len(lines),'Missing record'
        m=re.fullmatch(pattern,lines[at]);assert m,(at,lines[at],pattern)
        at+=1;return m
    take('BEGIN 149 2 3 32768');take('INIT_RETURN 0')
    for d in range(2):
        m=take(fr'ARENA {d} ([0-9a-f]{{8}}) 32768');base=int(m[1],16);assert 0<base<64*1024**2-SIZE
        pitch=128 if d else 256;other=192 if d else 320;off=2048 if d else 4096
        surfaces.append(dict(depth=bool(d),base=base,offset=off,pitch_a=pitch,pitch_b=other,bpp=2 if d else 4))
        take(f'BIND {d} 0 0 {pitch}');take(f'UNREAD_A {d}');take(f'BIND {d} 1 {off} {other}')
        take(f'CAPTURE {d} 0 32768');take(f'CPU_PATCH {d} 25');take(f'CAPTURE {d} 1 32768')
        take(f'BIND {d} 0 0 {pitch}');take(f'CAPTURE {d} 2 32768')
    take('KILL_RETURN');take('COMPLETE 6 50 0');take('NORMAL_REBOOT_REQUEST');assert at==len(lines)
    return surfaces

# Phase150 deliberately keeps pbkit alive until the external emulator reset.
def validate_before(data):
    lines=data.decode('ascii').splitlines()
    assert lines[0]=='BEGIN 150 2 3 32768'
    assert lines[-2:]==['COMPLETE 6 50 0','RESET_READY_REQUEST']
    assert 'KILL_RETURN' not in lines and 'NORMAL_REBOOT_REQUEST' not in lines
    normalized=['BEGIN 149 2 3 32768']+lines[1:-2]+['KILL_RETURN','COMPLETE 6 50 0','NORMAL_REBOOT_REQUEST']
    return validate_log(('\r\n'.join(normalized)+'\r\n').encode())
