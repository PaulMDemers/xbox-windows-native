"""Independent integer rectangle oracle, same-value disjoint CPU sentinel."""
import array,re,sys
W,H=640,480
def expected():
    p=array.array('I',[0xff15324a])*(W*H)
    for y in range(96,160):p[y*W+128:y*W+192]=array.array('I',[0xffff00ff])*64
    if sys.byteorder!='little':p.byteswap()
    return p.tobytes()
def compare(data):
    ref=expected()
    if data is None:return dict(matched=False,reason='missing')
    if len(data)!=len(ref):return dict(matched=False,reason='length',bytes=len(data))
    errors=[i for i in range(W*H) if data[4*i:4*i+4]!=ref[4*i:4*i+4]]
    return dict(matched=not errors,different_pixels=len(errors),first_difference=None if not errors else dict(x=errors[0]%W,y=errors[0]//W),
        drawn_pixels=sum(data[i:i+4]==b'\xff\x00\xff\xff' for i in range(0,len(data),4)))
def validate_log(data):
    lines=data.decode('ascii').splitlines();at=0
    def take(pattern):
        nonlocal at
        assert at<len(lines),'Missing line'
        m=re.fullmatch(pattern,lines[at]);assert m,(at,lines[at],pattern)
        at+=1;return m
    take('BEGIN 145 4 640 480');take('INIT_RETURN 0')
    m=take(r'SURFACE ([0-9a-f]{8}) 2560');base=int(m[1],16);assert 0<base<64*1024**2-W*H*4
    for mode in range(4):
        take(f'CASE {mode}');take(f'CLEAR_IDLE {mode}')
        if mode==1:take(f'CPU_STORE {mode} 3 5 ff15324a')
        take(f'BEGIN_IDLE {mode}')
        if mode==2:take(f'CPU_STORE {mode} 3 5 ff15324a')
        take(f'ARRAYS_IDLE {mode}')
        if mode==3:take(f'CPU_STORE {mode} 3 5 ff15324a')
        take(f'END_IDLE {mode}');take(f'CAPTURE {mode} 1228800')
    take('KILL_RETURN');take('COMPLETE 4 3 0');take('NORMAL_REBOOT_REQUEST');assert at==len(lines)
    return base
