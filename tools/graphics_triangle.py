#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent rung07 clear/interior/background oracle. No exact edge/alpha claim."""
import argparse
import json
from pathlib import Path
import struct
import uuid
from graphics_discovery import decode, integer, unhex

WIDTH = HEIGHT = 64
BG, FG = 0x102030, 0x40c080
HRESULTS = ('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
            'viewport state.z state.zwrite state.lighting state.cull state.fill state.shade '
            'state.fog state.alpha state.alphatest state.dither state.specular state.antialias '
            'texture0 stage0.op stage0.arg stage0.alpha stage1.op clear scene.begin draw scene.end '
            'clear_capture.lock clear_capture.unlock draw_capture.lock draw_capture.unlock').split()


def pixels(clear, draw):
    if len(clear) != 16384 or len(draw) != 16384:
        raise ValueError('Capture length')
    counts = dict(clear_pixels=0, interior_pixels=0, exterior_pixels=0, boundary_pixels=0)
    for y in range(64):
        for x in range(64):
            at = (y*64+x)*4
            a = int.from_bytes(clear[at:at+3], 'little')
            b = int.from_bytes(draw[at:at+3], 'little')
            if a != BG:
                raise ValueError(f'Clear pixel {x},{y}')
            counts['clear_pixels'] += 1
            # Deliberately well away from all three rasterization edges.
            if x >= 12 and y >= 12 and x+y <= 56:
                if b != FG:
                    raise ValueError(f'Interior pixel {x},{y}')
                counts['interior_pixels'] += 1
            elif x <= 4 or y <= 4 or x+y >= 72 or x >= 60 or y >= 60:
                if b != BG:
                    raise ValueError(f'Exterior pixel {x},{y}')
                counts['exterior_pixels'] += 1
            else:
                if b not in (BG, FG):
                    raise ValueError(f'Unexpected boundary color {x},{y}')
                counts['boundary_pixels'] += 1
    return counts


def validate(raw, clear, draw, backend, process_exit):
    if backend not in ('default', 'hel') or type(process_exit) is not int or process_exit != 0:
        raise ValueError('Backend/exit')
    f = decode(raw)
    exact = dict(schema='xwn-d3d-triangle-1', backend=backend, scope='offscreen-rgb-software',
                 width='64', height='64', exit='0', result='CAPTURED', end='complete',
                 **{'os.major':'5', 'os.minor':'0', 'os.build':'2195', 'window.created':'1',
                    'ddraw.load':'1', 'ddraw.entry':'1', 'ddraw.unload':'1',
                    'enum.matches':'1', 'enum.error':'0', 'vertex.stride':'20', 'vertex.fvf':'68',
                    'clear_capture.valid':'1', 'draw_capture.valid':'1', 'modules.ok':'1',
                    'modules.end_error':'18', 'release.device':'0', 'release.target':'0', 'release.ddraw':'0'})
    exact.update({k:'0' for k in HRESULTS})
    numeric = {'enum.count','release.d3d','modules','clear_capture.pitch','clear_capture.caps',
               'draw_capture.pitch','draw_capture.caps'}
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
    wanted = b''.join(struct.pack('<ffffI',x,y,.5,1,0xff40c080) for x,y in [(8,8),(56,8),(8,56)])
    if unhex(f['vertices'],60,60) != wanted:
        raise ValueError('Vertex transport')
    for stage in ('clear_capture','draw_capture'):
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
    return dict(passed=True, backend=backend, modules=modules, **pixels(clear,draw),
                scope='RGB software offscreen clear and safe interior/exterior RGB; alpha, exact edges, presentation and speed unqualified')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=['default','hel'],required=True)
    a=p.parse_args();s=str(a.prefix)
    result=validate(Path(s+'.txt').read_bytes(),Path(s+'-clear.bin').read_bytes(),
                    Path(s+'-draw.bin').read_bytes(),a.backend,int(Path(s+'.exit').read_text()))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
