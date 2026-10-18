#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent rung08c source-alpha oracle with predefined 8-bit rounding bounds."""
import argparse
import json
from pathlib import Path
import struct
import uuid
from graphics_discovery import decode, integer, unhex

WIDTH = HEIGHT = 64
BG, FG = 0x102030, 0x40c080
STAGES = ('clear', 'a0', 'a85', 'a170', 'a255', 'disabled')
SUFFIXES = STAGES
ALPHAS = (0, 0, 85, 170, 255, 85)
BG, FG = 0x00ff00, 0xff00ff
HRESULTS = ('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
            'viewport state.z state.zwrite state.lighting state.cull state.fill state.shade '
            'state.fog state.alpha state.alphatest state.dither state.specular state.antialias '
            'texture0 stage0.op stage0.arg stage0.alpha stage0.alpha_arg stage1.op state.src state.dest').split()
for stage in STAGES:
    HRESULTS += [stage+'.'+k for k in ('set_blend','get_blend','get_src','get_dest','clear_hr','lock','unlock')]
    if stage != 'clear': HRESULTS += [stage+'.'+k for k in ('begin','draw','end')]


def allowed(stage):
    if stage in ('clear', 'a0'): return {BG}
    if stage in ('a255', 'disabled'): return {FG}
    a = 85 if stage == 'a85' else 170
    # Frozen BEFORE execution: ideal RGB=(a,255-a,a), one 8-bit level each way.
    return {(r<<16)|(g<<8)|b for r in range(a-1,a+2)
            for g in range(254-a,257-a) for b in range(a-1,a+2)}


def pixels(*frames):
    if len(frames)!=6 or any(len(f)!=16384 for f in frames): raise ValueError('Capture length/count')
    result={}
    for stage,frame in zip(STAGES,frames):
        wanted=allowed(stage);edge=wanted|{BG};counts=dict(interior_pixels=0,exterior_pixels=0,boundary_pixels=0)
        for index,(raw,) in enumerate(struct.iter_unpack('<I',frame)):
            x,y=index%64,index//64;color=raw&0xffffff
            if x>=12 and y>=12 and x+y<=56: colors=wanted;kind='interior_pixels'
            elif x<=4 or y<=4 or x+y>=72 or x>=60 or y>=60: colors={BG};kind='exterior_pixels'
            else: colors=edge;kind='boundary_pixels'
            if color not in colors: raise ValueError(f'{stage} pixel {x},{y}')
            counts[kind]+=1
        result[stage]=counts
    return result


def validate(raw, frames, backend, process_exit):
    if backend not in ('default', 'hel') or type(process_exit) is not int or process_exit != 0:
        raise ValueError('Backend/exit')
    f = decode(raw)
    exact = dict(schema='xwn-d3d-blend-1', backend=backend, scope='offscreen-rgb-software',
                 width='64', height='64', exit='0', result='CAPTURED', end='complete',
                 **{'os.major':'5', 'os.minor':'0', 'os.build':'2195', 'window.created':'1',
                    'ddraw.load':'1', 'ddraw.entry':'1', 'ddraw.unload':'1',
                    'enum.matches':'1', 'enum.error':'0', 'vertex.stride':'20', 'vertex.fvf':'68',
                    'modules.ok':'1',
                    'modules.end_error':'18', 'release.device':'0', 'release.target':'0', 'release.ddraw':'0'})
    exact.update({k:'0' for k in HRESULTS})
    for i,stage in enumerate(STAGES):
        exact.update({stage+'.valid':'1',stage+'.alpha':str(ALPHAS[i]),stage+'.blend':'0' if i==5 else '1',stage+'.src':'5',stage+'.dest':'6'})
    numeric = {'enum.count','release.d3d','modules'} | {stage+'.'+k for stage in STAGES for k in ('pitch','caps')}
    n = integer(f.get('modules','?'))
    if not 1 <= n <= 64 or not 1 <= integer(f.get('enum.count','?')) <= 16:
        raise ValueError('Inventory capacity')
    extra = {'device.caps','vertices'} | {f'module{i}.{k}' for i in range(n) for k in ('path','bytes')}
    if set(f) != set(exact) | numeric | extra or any(f[k] != v for k,v in exact.items()):
        raise ValueError('Incomplete, unknown or failed field')
    for k in numeric:
        integer(f[k])
    caps = unhex(f['device.caps'],236,236)
    if uuid.UUID(bytes_le=caps[196:212]) != uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356'):
        raise ValueError('Unenumerated RGB identity')
    if struct.unpack_from('<I',caps)[0] & 0x90000 or not struct.unpack_from('<I',caps,116)[0] & 0x100:
        raise ValueError('Hardware flag or unsupported depth')
    if not struct.unpack_from('<I',caps,76)[0]&0x10 or not struct.unpack_from('<I',caps,80)[0]&0x20:
        raise ValueError('Missing enumerated blend factors')
    wanted = b''.join(struct.pack('<ffffI',x,y,.5,1,(a<<24)|FG) for a in (0,85,170,255,85) for x,y in [(8,8),(56,8),(8,56)])
    if unhex(f['vertices'],300,300) != wanted:
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
    return dict(passed=True, backend=backend, modules=modules, pixel_checks=pixels(*frames),
                scope='RGB software SRCALPHA/INVSRCALPHA diffuse blending; partial RGB allows one level rounding; exact edges, destination alpha, presentation and speed unqualified')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=['default','hel'],required=True)
    a=p.parse_args();s=str(a.prefix)
    result=validate(Path(s+'.txt').read_bytes(),[Path(s+'-'+suffix+'.bin').read_bytes() for suffix in SUFFIXES],a.backend,int(Path(s+'.exit').read_text()))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
