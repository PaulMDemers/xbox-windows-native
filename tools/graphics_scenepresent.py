#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rung 09c: independent scene pixels plus exact clipped GDI presentation."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import graphics_scene as scene

SUFFIXES=('clear','draw','source-before','source-after','screen-before','screen-after','post','native-before','native-after')

def validate(raw,clear,draw,source_before,source_after,screen_before,screen_after,post,native_before,native_after,backend,process_exit):
    f=scene.decode(raw); seen=set()
    def need(k,v):
        seen.add(k)
        if f.get(k)!=str(v):raise ValueError('Presentation field: '+k)
    def num(k):
        seen.add(k);return scene.integer(f.get(k,'?'))
    need('schema','xwn-scene-present-2')
    need('scope','windowed-xyz-texture-depth-rgb-software')
    base={k:v for k,v in f.items() if not k.startswith('p.')}
    base['schema']='xwn-d3d-scene-1';base['scope']='offscreen-xyz-texture-depth-rgb-software'
    # Reuse the strict scene metadata and independent geometric oracle unchanged.
    result=scene.validate(''.join(k+'='+v+'\r\n' for k,v in base.items()).encode(),
                          clear,draw,source_before,source_after,backend,process_exit)
    for k in ('mode','primary.create','primary.format','clipper.create','clipper.hwnd',
              'clipper.gethwnd','primary.clipper','primary.detach','release.primary','release.clipper','bridge.create','release.bridge'):
        need('p.'+k,0)
    need('p.clipper.owner',1);bits=num('p.mode.bits')
    if not 640<=num('p.mode.width')<=4096 or not 480<=num('p.mode.height')<=2160:
        raise ValueError('Desktop bounds')
    seen.add('p.format');fmt=struct.unpack('<8I',scene.unhex(f.get('p.format',''),32,32))
    valid={(32,64,0,32,0xff0000,0xff00,255,0),(32,64,0,16,0xf800,0x7e0,31,0),(32,64,0,16,0x7c00,0x3e0,31,0)}
    if fmt not in valid or bits!=fmt[3]:raise ValueError('Native format')
    def packed(v):
        if bits==32:return v&0xffffff
        red=(v>>16)&255;green=(v>>8)&255;blue=v&255
        return ((red//8)<<11)|((green//4)<<5)|(blue//8) if fmt[4]==0xf800 else ((red//8)<<10)|((green//8)<<5)|(blue//8)
    if len(screen_before)!=5*80*80*4 or len(screen_after)!=len(screen_before) or len(post)!=len(draw):
        raise ValueError('Presentation capture lengths')
    if len(native_before)!=len(draw) or len(native_after)!=len(draw):raise ValueError('Native capture lengths')
    native=tuple(packed(v) for v in struct.unpack('<20480I',draw))
    if struct.unpack('<20480I',native_before)!=native or struct.unpack('<20480I',native_after)!=native:
        raise ValueError('Native upload/preservation')
    pixels=struct.unpack('<20480I',draw); after_source=struct.unpack('<20480I',post)
    if any((a&0xffffff)!=(b&0xffffff) for a,b in zip(pixels,after_source)):
        raise ValueError('Presentation changed source')
    screens=[struct.unpack('<32000I',b) for b in (screen_before,screen_after)]
    for i in range(5):
        p=f'p.s{i}.';ox,oy=(144,112) if i>=2 else (64,64);covered=i in (1,2)
        need(p+'origin.x',ox);need(p+'origin.y',oy)
        for k in ('cover','cover.visible'):need(p+k,int(covered))
        for k in ('cover.above','clip.exact','complete','before.capture','after.capture','post.valid'):need(p+k,1)
        for k in ('clip.size','clip.list','primary.blit','before.mismatches','after.mismatches','post.lock','post.unlock'):need(p+k,0)
        pitch=num(p+'post.pitch');caps=num(p+'post.caps')
        if not 256<=pitch<=4096 or pitch%4 or caps&0x2840!=0x2840 or caps&0x4200:
            raise ValueError('Post source ownership')
        for when in range(2):
            for k in ('lock','unlock','mismatches'):need(p+f'native{when}.'+k,0)
            need(p+f'native{when}.valid',1)
            pitch=num(p+f'native{when}.pitch');caps=num(p+f'native{when}.caps')
            if not 64*(bits//8)<=pitch<=4096 or pitch%(bits//8) or caps&0x840!=0x840 or caps&0x4200:
                raise ValueError('Native surface ownership')
        count=num(p+'clip.count')
        if not 1<=count<=64:raise ValueError('Clip capacity')
        need(p+'clip.bytes',32+16*count)
        rects=[]
        for j in range(count):
            left,top,right,bottom=[num(p+f'clip.r{j}.'+e) for e in ('left','top','right','bottom')]
            if not ox+8<=left<right<=ox+56 or not oy+8<=top<bottom<=oy+56:
                raise ValueError('Clip bounds')
            rects.append((left,top,right,bottom))
        for y in range(80):
            for x in range(80):
                target=8<=x<56 and 8<=y<56
                occluded=covered and 24<=x<48 and 24<=y<48
                hits=sum(l<=ox+x<r and t<=oy+y<b for l,t,r,b in rects)
                if hits!=int(target and not occluded):raise ValueError('Clip union/overlap')
                baseline=packed(0xff00ff) if occluded else 0 if target else packed(255)
                expected=packed(pixels[i*4096+y*64+x]) if target and not occluded else baseline
                offset=i*6400+y*80+x
                if screens[0][offset]!=baseline or screens[1][offset]!=expected:
                    raise ValueError(f'GDI pixel mismatch: stage {i}, ({x},{y})')
    if {k for k in f if k.startswith('p.')}!={k for k in seen if k.startswith('p.')}:
        raise ValueError('Unknown presentation metadata')
    result.update(report_sha256=hashlib.sha256(raw).hexdigest(),presentation_native_samples=5*80*80*2,native_format=list(fmt),
                  source_post_rgb_bytes=5*64*64*3,
                  scope='Five RGB software scene cases and explicit native CPU upload and exact clipped native GDI readback through cover/move/uncover. No GPU, performance, varying-W or game qualification.')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=('default','hel'),required=True);a=p.parse_args();s=str(a.prefix)
    print(json.dumps(validate(Path(s+'.txt').read_bytes(),*[Path(s+'-'+n+'.bin').read_bytes() for n in SUFFIXES],
                              a.backend,int(Path(s+'.exit').read_text(encoding='utf-8'))),indent=2))
if __name__=='__main__':main()
