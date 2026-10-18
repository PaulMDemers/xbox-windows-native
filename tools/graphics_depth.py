#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent rung08b depth/order/clear oracle. No exact edge/alpha claim."""
import argparse
import json
from pathlib import Path
import struct
import uuid
from graphics_discovery import decode, integer, unhex

WIDTH = HEIGHT = 64
BG, FG = 0x102030, 0x40c080
FAR = 0xc04080
STAGES = ('clear','far_near','near_far','no_z','zero_z')
SUFFIXES = ('clear','far-near','near-far','no-z','zero-z')
HRESULTS = ('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
            'viewport state.z state.zwrite state.zfunc state.lighting state.cull state.fill state.shade '
            'state.fog state.alpha state.alphatest state.dither state.specular state.antialias '
            'texture0 stage0.op stage0.arg stage0.alpha stage1.op formats.hr depth.create depth.desc '
            'depth.attach depth.get_attached depth.detach').split()
for stage in STAGES:
    HRESULTS += [stage+'.'+k for k in ('state_z','clear_hr','lock','unlock')]
    if stage!='clear':
        HRESULTS += [stage+'.'+k for k in ('begin','draw0.hr','draw1.hr','end')]


def pixels(*frames):
    if len(frames)!=5 or any(len(f)!=16384 for f in frames):
        raise ValueError('Capture count/length')
    result={}
    for stage,frame in zip(STAGES,frames):
        fg = FAR if stage=='no_z' else BG if stage in ('clear','zero_z') else FG
        counts=dict(interior_pixels=0,exterior_pixels=0,boundary_pixels=0)
        for y in range(64):
            for x in range(64):
                at=(y*64+x)*4; color=int.from_bytes(frame[at:at+3],'little')
                if x>=12 and y>=12 and x+y<=56:
                    wanted=(fg,);kind='interior_pixels'
                elif x<=4 or y<=4 or x+y>=72 or x>=60 or y>=60:
                    wanted=(BG,);kind='exterior_pixels'
                else:
                    wanted=(BG,fg);kind='boundary_pixels'
                if color not in wanted:raise ValueError(f'{stage} pixel {x},{y}')
                counts[kind]+=1
        result[stage]=counts
    return result


def acceptable(raw):
    v=struct.unpack('<8I',raw)
    return v[0]==32 and v[1]==0x400 and v[2]==0 and v[3] in (16,24,32) and v[4]==0 and v[6]==0


def validate(raw, frames, backend, process_exit):
    if backend not in ('default', 'hel') or type(process_exit) is not int or process_exit != 0:
        raise ValueError('Backend/exit')
    f = decode(raw)
    exact = dict(schema='xwn-d3d-depth-1', backend=backend, scope='offscreen-rgb-software',
                 width='64', height='64', exit='0', result='CAPTURED', end='complete',
                 **{'os.major':'5', 'os.minor':'0', 'os.build':'2195', 'window.created':'1',
                    'ddraw.load':'1', 'ddraw.entry':'1', 'ddraw.unload':'1',
                    'enum.matches':'1', 'enum.error':'0', 'vertex.stride':'20', 'vertex.fvf':'68',
                    'depth.identity':'1', 'depth.width':'64', 'depth.height':'64', 'formats.error':'0', 'release.depth':'0', 'modules.ok':'1',
                    'modules.end_error':'18', 'release.device':'0', 'release.target':'0', 'release.ddraw':'0'})
    exact.update({k:'0' for k in HRESULTS})
    for stage in STAGES:
        exact.update({stage+'.valid':'1',stage+'.z_enabled':'0' if stage=='no_z' else '1',stage+'.clear_z':'0' if stage=='zero_z' else '1'})
        if stage!='clear':
            exact.update({stage+'.draw0.index':'1' if stage=='far_near' else '0',stage+'.draw1.index':'0' if stage=='far_near' else '1'})
    numeric = {'enum.count','release.d3d','modules','depth.caps','depth.release_query','formats.count','formats.selected'} | {stage+'.'+k for stage in STAGES for k in ('pitch','caps')}
    count=integer(f.get('formats.count','?'));selected=integer(f.get('formats.selected','?'))
    if not 1<=count<=64 or not 0<=selected<count:raise ValueError('Depth format capacity/selection')
    n = integer(f.get('modules','?'))
    if not 1 <= n <= 64 or not 1 <= integer(f.get('enum.count','?')) <= 16:
        raise ValueError('Inventory capacity')
    extra = {'device.caps','vertices','depth.format'} | {f'format{i}' for i in range(count)} | {f'module{i}.{k}' for i in range(n) for k in ('path','bytes')}
    if set(f) != set(exact) | numeric | extra or any(f[k] != v for k,v in exact.items()):
        raise ValueError('Incomplete, unknown or failed field')
    for k in numeric:
        integer(f[k])
    caps = unhex(f['device.caps'],236,236)
    if uuid.UUID(bytes_le=caps[196:212]) != uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356'):
        raise ValueError('Unenumerated RGB identity')
    if struct.unpack_from('<I',caps)[0] & 0x90000 or not struct.unpack_from('<I',caps,116)[0] & 0x100:
        raise ValueError('Hardware flag or unsupported depth')
    formats=[unhex(f[f'format{i}'],32,32) for i in range(count)]
    if any(struct.unpack_from('<I',v)[0]!=32 for v in formats):raise ValueError('Depth format size')
    possible=[i for i,v in enumerate(formats) if acceptable(v)]
    if not possible or selected!=possible[0] or unhex(f['depth.format'],32,32)!=formats[selected]:raise ValueError('Depth format provenance')
    c=integer(f['depth.caps'])
    if c&0x20800!=0x20800 or c&0x4200 or integer(f['depth.release_query'])<1:raise ValueError('Depth ownership')
    wanted = b''.join(struct.pack('<ffffI',x,y,z,1,color) for z,color in [(.25,0xff40c080),(.75,0xffc04080)] for x,y in [(8,8),(56,8),(8,56)])
    if unhex(f['vertices'],120,120) != wanted:
        raise ValueError('Vertex transport')
    for stage in STAGES:
        c=integer(f[stage+'.caps'])
        if c & 0x2840 != 0x2840 or c & 0x4200 or not 256 <= integer(f[stage+'.pitch']) <= 4096:
            raise ValueError('Surface ownership/pitch')
    modules=[]
    for i in range(n):
        name=unhex(f[f'module{i}.path'],1,259).decode('ascii')
        if not name.lower().startswith('c:\\') or '..' in name.split('\\') or '/' in name or not integer(f[f'module{i}.bytes']):
            raise ValueError('Module path/size')
        if name.lower() in [p.lower() for p in modules]:
            raise ValueError('Duplicate module')
        modules.append(name)
    if not any(p.lower().endswith('\\ddraw.dll') for p in modules):
        raise ValueError('Missing live runtime module')
    return dict(passed=True, backend=backend, modules=modules, pixel_checks=pixels(*frames), depth_format=struct.unpack('<8I',formats[selected]),
                scope='RGB software depth LESS/write, two draw orders, depth disabled and clear-zero controls; stencil, exact edges, alpha, presentation and speed unqualified')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=['default','hel'],required=True)
    a=p.parse_args();s=str(a.prefix)
    result=validate(Path(s+'.txt').read_bytes(),[Path(s+'-'+n+'.bin').read_bytes() for n in SUFFIXES],a.backend,int(Path(s+'.exit').read_text()))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
