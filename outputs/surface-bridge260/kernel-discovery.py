"""Next-attempt helper: derive a kernel base from two actual x86 IDT gates.

No scanning arbitrary RAM and no replacement of a failed historical base guess.
The caller must record IDTR from the actual stopped CPU, then pin PE identity and
both resident trap entries with the matching owned PDB/binary before accepting.
This helper has NOT been used in a guest run.
"""
import struct

def discover(read,idt_base,idt_limit,trap_rvas):
    assert 0x80000000<=idt_base<=0xfffff800 and idt_limit>=15*8-1
    rows=[];bases=[]
    for vector in (0,14):
        raw=read(idt_base+8*vector,8);assert len(raw)==8
        lo,selector,zero,flags,hi=struct.unpack('<HHBBH',raw)
        assert zero==0 and selector and not selector&7
        assert flags&0x80 and not flags&0x10 and flags&15 in (14,15)
        address=lo+(hi<<16);rva=trap_rvas[vector];assert 0<rva<0x200000
        base=address-rva;assert 0x80000000<=base<=0xff000000 and not base&4095
        rows.append(dict(vector=vector,raw=raw.hex(),selector=selector,flags=flags,address=address,rva=rva,base=base));bases.append(base)
    assert bases[0]==bases[1],'Independent trap vectors disagree'
    return bases[0],rows
