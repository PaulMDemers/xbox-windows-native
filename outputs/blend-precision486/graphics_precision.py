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
STAGES = ('clear', 'zeroone', 'onezero', 'a0', 'a85', 'a170', 'a255', 'disabled')
SUFFIXES = STAGES
ALPHAS = (0,85,85,0,85,170,255,85)
SOURCES = (5,1,2,5,5,5,5,5)
DESTINATIONS = (6,2,1,6,6,6,6,6)
BG, FG = 0x2468ac, 0xc97539
HRESULTS = ('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
            'viewport state.z state.zwrite state.lighting state.cull state.fill state.shade '
            'state.fog state.alpha state.alphatest state.dither state.specular state.antialias '
            'texture0 stage0.op stage0.arg stage0.alpha stage0.alpha_arg stage1.op state.src state.dest').split()
for stage in STAGES:
    HRESULTS += [stage+'.'+k for k in ('set_src','set_dest','set_blend','get_blend','get_src','get_dest','clear_hr','lock','unlock')]
    if stage != 'clear': HRESULTS += [stage+'.'+k for k in ('begin','draw','end')]


MODELS=('ideal_nearest255','combined_floor256','separate_floor256')
def expected(stage,model):
    if stage in ('clear','zeroone'):return BG
    if stage in ('onezero','disabled'):return FG
    alpha=ALPHAS[STAGES.index(stage)];rgb=0
    for shift in (16,8,0):
        source=(FG>>shift)&255;dest=(BG>>shift)&255
        if model=='ideal_nearest255':v=(source*alpha+dest*(255-alpha)+127)//255
        elif model=='combined_floor256':v=(source*alpha+dest*(255-alpha))//256
        elif model=='separate_floor256':v=source*alpha//256+dest*(255-alpha)//256
        else:raise ValueError('Unknown arithmetic model')
        rgb|=v<<shift
    return rgb
def pixels(*frames):
    if len(frames)!=8 or any(len(f)!=16384 for f in frames):raise ValueError('Capture length/count')
    matching=[]
    for model in MODELS:
        valid=True
        for stage,frame in zip(STAGES,frames):
            want=expected(stage,model)
            for index,(word,) in enumerate(struct.iter_unpack('<I',frame)):
                x,y=index%64,index//64;rgb=word&0xffffff
                if x>=12 and y>=12 and x+y<=56:allowed={want}
                elif x<=4 or y<=4 or x+y>=72 or x>=60 or y>=60:allowed={BG}
                else:allowed={BG,want}
                if rgb not in allowed:valid=False;break
            if not valid:break
        if valid:matching.append(model)
    if len(matching)!=1:raise ValueError('No unique predefined arithmetic model: '+repr(matching))
    return dict(characterization_only=True,matching_model=matching[0],original_484_requalified=False,strict_ideal_model=matching[0]=='ideal_nearest255')

def validate(raw, frames, backend, process_exit):
    if backend not in ('default', 'hel') or type(process_exit) is not int or process_exit != 0:
        raise ValueError('Backend/exit')
    f = decode(raw)
    exact = dict(schema='xwn-d3d-precision-1', backend=backend, scope='offscreen-rgb-software',
                 width='64', height='64', exit='0', result='CAPTURED', end='complete',
                 **{'os.major':'5', 'os.minor':'0', 'os.build':'2195', 'window.created':'1',
                    'ddraw.load':'1', 'ddraw.entry':'1', 'ddraw.unload':'1',
                    'enum.matches':'1', 'enum.error':'0', 'vertex.stride':'20', 'vertex.fvf':'68',
                    'modules.ok':'1',
                    'modules.end_error':'18', 'release.device':'0', 'release.target':'0', 'release.ddraw':'0'})
    exact.update({k:'0' for k in HRESULTS})
    for i,stage in enumerate(STAGES):
        exact.update({stage+'.valid':'1',stage+'.alpha':str(ALPHAS[i]),stage+'.blend':'0' if i==7 else '1',stage+'.src':str(SOURCES[i]),stage+'.dest':str(DESTINATIONS[i])})
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
    wanted = b''.join(struct.pack('<ffffI',x,y,.5,1,(a<<24)|FG) for a in (85,85,0,85,170,255,85) for x,y in [(8,8),(56,8),(8,56)])
    if unhex(f['vertices'],420,420) != wanted:
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
                scope='Fixed mixed-color arithmetic characterization; not exact alpha qualification or an implementation trace')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=['default','hel'],required=True)
    a=p.parse_args();s=str(a.prefix)
    result=validate(Path(s+'.txt').read_bytes(),[Path(s+'-'+suffix+'.bin').read_bytes() for suffix in SUFFIXES],a.backend,int(Path(s+'.exit').read_text()))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
