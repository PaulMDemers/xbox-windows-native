#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rung08a: independent 8x8 texture upload, orientation and point-sampling oracle."""
import argparse
import json
from pathlib import Path
import struct
import uuid
from graphics_discovery import decode, integer, unhex

BG=0x102030
HRESULTS=('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
 'viewport formats.hr texture.create state.z state.zwrite state.lighting state.cull '
 'state.fill state.shade state.fog state.alpha state.alphatest state.dither state.specular '
 'state.antialias texture0 stage0.op stage0.arg stage0.alpha stage1.op stage0.min '
 'stage0.mag stage0.mip stage0.u stage0.v stage0.coord stage0.transform clear scene.begin '
 'draw scene.end texture.unbind clear_capture.lock clear_capture.unlock '
 'draw_capture.lock draw_capture.unlock source_before.lock source_before.unlock '
 'source_after.lock source_after.unlock').split()


def color(x,y):
    return ((32+24*x)<<16)|((32+24*y)<<8)|(224 if (x+y)%2 else 32)


def acceptable(raw):
    size,flags,fourcc,bits,r,g,b,a=struct.unpack('<8I',raw)
    return (size==32 and flags in (64,65) and fourcc==0 and bits==32 and
            (r,g,b)==(0xff0000,0xff00,0xff) and a==(0xff000000 if flags==65 else 0))


def pixels(clear,draw,before,after,alpha=False):
    if len(clear)!=16384 or len(draw)!=16384 or len(before)!=256 or len(after)!=256:
        raise ValueError('Capture length')
    expected=b''.join(struct.pack('<I',color(x,y)|(0xff000000 if alpha else 0))
                      for y in range(8) for x in range(8))
    if before!=expected or after!=before:
        raise ValueError('Texture upload, orientation or unchanged bytes')
    palette={color(x,y) for y in range(8) for x in range(8)}|{BG}
    counts=dict(clear_pixels=0,interior_pixels=0,exterior_pixels=0,boundary_pixels=0,
                source_bytes=512)
    for y in range(64):
        for x in range(64):
            at=(y*64+x)*4
            a=int.from_bytes(clear[at:at+3],'little')
            b=int.from_bytes(draw[at:at+3],'little')
            if a!=BG:raise ValueError(f'Clear {x},{y}')
            counts['clear_pixels']+=1
            # Interior 3x3 of each six-pixel texel cell: excludes raster and
            # nearest-neighbor boundaries. Both triangles use identical affine UV.
            if 8<=x<56 and 8<=y<56 and (x-8)%6 in (2,3,4) and (y-8)%6 in (2,3,4):
                if b!=color((x-8)//6,(y-8)//6):raise ValueError(f'Texel {x},{y}')
                counts['interior_pixels']+=1
            elif x<=4 or y<=4 or x>=60 or y>=60:
                if b!=BG:raise ValueError(f'Exterior {x},{y}')
                counts['exterior_pixels']+=1
            else:
                if b not in palette:raise ValueError(f'Boundary color {x},{y}')
                counts['boundary_pixels']+=1
    return counts


def validate(raw,clear,draw,before,after,backend,process_exit):
    if backend not in ('default','hel') or type(process_exit) is not int or process_exit!=0:
        raise ValueError('Backend/exit')
    f=decode(raw)
    exact=dict(schema='xwn-d3d-texture-1',backend=backend,scope='offscreen-rgb-software',
               width='64',height='64',exit='0',result='CAPTURED',end='complete',
               **{'os.major':'5','os.minor':'0','os.build':'2195','window.created':'1',
                  'ddraw.load':'1','ddraw.entry':'1','ddraw.unload':'1','enum.matches':'1',
                  'enum.error':'0','formats.error':'0','vertex.stride':'24','vertex.fvf':'260',
                  'modules.ok':'1','modules.end_error':'18','release.device':'0',
                  'release.texture':'0','release.target':'0','release.ddraw':'0'})
    exact.update({k:'0' for k in HRESULTS})
    stages=('clear_capture','draw_capture','source_before','source_after')
    exact.update({k+'.valid':'1' for k in stages})
    numeric={'enum.count','release.d3d','modules','formats.count','formats.selected'}
    numeric|={s+'.'+k for s in stages for k in ('pitch','caps')}
    n=integer(f.get('modules','?'));nf=integer(f.get('formats.count','?'))
    if not 1<=n<=64 or not 1<=nf<=64 or not 1<=integer(f.get('enum.count','?'))<=16:
        raise ValueError('Inventory capacity')
    extra={'device.caps','vertices','source_before.format','source_after.format'}
    extra|={f'module{i}.{k}' for i in range(n) for k in ('path','bytes')}
    extra|={f'format{i}' for i in range(nf)}
    if set(f)!=set(exact)|numeric|extra or any(f[k]!=v for k,v in exact.items()):
        raise ValueError('Incomplete, unknown or failed field')
    for k in numeric:integer(f[k])
    caps=unhex(f['device.caps'],236,236)
    if uuid.UUID(bytes_le=caps[196:212])!=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356'):
        raise ValueError('Unenumerated RGB identity')
    if struct.unpack_from('<I',caps)[0]&0x90000 or not struct.unpack_from('<I',caps,116)[0]&0x100:
        raise ValueError('Hardware flag or unsupported depth')
    fmt=[unhex(f[f'format{i}'],32,32) for i in range(nf)]
    if any(struct.unpack_from('<I',v)[0]!=32 for v in fmt):raise ValueError('Format size')
    eligible=[i for i,v in enumerate(fmt) if acceptable(v)]
    if not eligible or integer(f['formats.selected'])!=eligible[0]:raise ValueError('Format selection')
    selected=fmt[eligible[0]]
    for s in ('source_before','source_after'):
        if unhex(f[s+'.format'],32,32)!=selected:raise ValueError('Unenumerated texture format')
    points=[(8,8,0,0),(56,8,1,0),(8,56,0,1),(8,56,0,1),(56,8,1,0),(56,56,1,1)]
    wanted=b''.join(struct.pack('<6f',x,y,.5,1,u,v) for x,y,u,v in points)
    if unhex(f['vertices'],144,144)!=wanted:raise ValueError('Vertex transport')
    for s in stages:
        c=integer(f[s+'.caps']);source=s.startswith('source')
        required=0x1800 if source else 0x2840
        if c&required!=required or c&(0x404200 if source else 0x4200):
            raise ValueError('Surface ownership')
        if not (32 if source else 256)<=integer(f[s+'.pitch'])<=4096:raise ValueError('Surface pitch')
    modules=[]
    for i in range(n):
        name=unhex(f[f'module{i}.path'],1,259).decode('ascii')
        if not name.lower().startswith('c:\\') or '..' in name.split('\\') or '/' in name or not integer(f[f'module{i}.bytes']):
            raise ValueError('Module path/size')
        if name.lower() in [p.lower() for p in modules]:raise ValueError('Duplicate module')
        modules.append(name)
    if not any(p.lower().endswith('\\ddraw.dll') for p in modules):raise ValueError('Missing runtime')
    return dict(passed=True,backend=backend,modules=modules,texture_formats=nf,
                selected_format=selected.hex(),**pixels(clear,draw,before,after,selected[4]==65),
                scope='Owned RGB software point texture, safe interiors and unchanged upload; exact edges, presentation, depth, blend, speed and GPU unqualified')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=['default','hel'],required=True);a=p.parse_args();s=str(a.prefix)
    result=validate(Path(s+'.txt').read_bytes(),*[Path(s+suffix).read_bytes() for suffix in
                    ('-clear.bin','-draw.bin','-source-before.bin','-source-after.bin')],
                    a.backend,int(Path(s+'.exit').read_text()))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
