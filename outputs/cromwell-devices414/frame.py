"""Bounds for this pinned 720p software framebuffer, not a display timing oracle."""
import struct


def geometry(mode, register):
    assert len(mode)==60 and type(register) is int and 0 <= register <= 0xffffffff
    fb,mmio,width,height=struct.unpack_from('<IIII',mode,8)
    assert mmio==0xfd000000 and fb==0xf3700000
    assert (width,height,mode[56])==(1280,720,32)
    address=fb&0x0fffffff
    assert register&0x0fffffff==address
    pitch=width*4
    size=pitch*height
    assert 0 < size <= 4*1024*1024 and address+size<=64*1024*1024
    return dict(address=address,width=width,height=height,pitch=pitch,bytes=size,
                source='Actual vmode plus framebuffer register agreement; pinned software drawing layout')
