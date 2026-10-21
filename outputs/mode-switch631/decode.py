"""Strict standalone631 result decoder; no successful exit implies a picture."""
import re,zlib
from oracle import oracle

CR=(0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39)
MM=(0x600804,0x680508,0x680600)
MODES=((720,480),(1280,720),(720,480))

def decode(data):
    lines=data.decode('ascii').splitlines()
    assert lines and re.fullmatch(r'XWN_HD631 version=1 kernel=\d+\.\d+\.\d+\.\d+',lines[0])
    assert lines[-1]=='COMPLETE error=0 log_ok=1 mode_changes=3'
    at=1
    def take(pattern):
        nonlocal at
        assert at<len(lines)
        m=re.fullmatch(pattern,lines[at]);assert m,lines[at]
        at+=1;return m.groups()
    settings=int(take(r'SETTINGS value=([0-9a-f]{8})')[0],16)
    assert settings&255==4 and settings&0xa0000==0xa0000
    result=[]
    for stage,(w,h) in enumerate(MODES,1):
        a=take(r'SET stage=(\d+) width=(\d+) height=(\d+) tick=(\d+)')
        assert tuple(map(int,a[:3]))==(stage,w,h)
        a=take(r'MODE stage=(\d+) width=(\d+) height=(\d+) bytes=(\d+) allocation=(\d+) physical=([0-9a-f]{8}) scanout=([0-9a-f]{8}) hvalid=(\d+) vvalid=(\d+) mismatches=(\d+) crc=([0-9a-f]{8}) tick=(\d+)')
        assert tuple(map(int,a[:4]))==(stage,w,h,w*h*4)
        allocation,pa,scanout=int(a[4]),int(a[5],16),int(a[6],16)
        assert w*h*4<=allocation<=w*h*4+4095
        assert 0<pa<64*1024**2-w*h*4 and pa==scanout
        assert tuple(map(int,a[7:10]))==(w-1,h-1,0)
        crc=int(a[10],16);assert crc==zlib.crc32(oracle(w,h))
        fp=[]
        for i in range(16):
            x=take(r'FP stage=(\d+) index=(\d+) value=([0-9a-f]{8})')
            assert tuple(map(int,x[:2]))==(stage,i);fp.append(int(x[2],16))
        assert fp[6]==h-1 and fp[14]==w-1
        x=take(r'TIMING stage=(\d+) index_before=(\d+) index_after=(\d+) flags_before=([0-9a-f]{8}) flags_after=([0-9a-f]{8})')
        assert int(x[0])==stage and 0<=int(x[1])<=255 and x[1]==x[2]
        assert not (int(x[3],16)^int(x[4],16))&0x200
        cr={};mm={}
        for i in CR:
            x=take(r'CRTC stage=(\d+) index=([0-9a-f]{2}) value=([0-9a-f]{2})')
            assert int(x[0])==stage and int(x[1],16)==i;cr[i]=int(x[2],16)
        for i in MM:
            x=take(r'MMIO stage=(\d+) offset=([0-9a-f]{8}) value=([0-9a-f]{8})')
            assert int(x[0])==stage and int(x[1],16)==i;mm[i]=int(x[2],16)
        pitch=8*(((cr[0x19]&0xe0)<<3)|cr[0x13])
        assert pitch==w*4 and cr[0x28]&15==3 and cr[0x39]==255
        x=take(r'GEOMETRY stage=(\d+) pitch=(\d+) format=(\d+) interlace=([0-9a-f]{2})')
        assert tuple(map(int,x[:3]))==(stage,pitch,3) and int(x[3],16)==255
        result.append(dict(stage=stage,width=w,height=h,pitch=pitch,crc=f'{crc:08x}',crtc=cr,mmio=mm,fp=fp))
    assert at==len(lines)-1
    return dict(passed=True,settings=settings,stages=result,visual_output='requires separate observation',windows_mode_switching=False)
