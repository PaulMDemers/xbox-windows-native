#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently verify D3D windowed reports and private source/GDI pixel captures."""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def decode(raw):
    if len(raw) > 65536 or not raw.endswith(b'end=complete\r\n'):
        raise ValueError('Incomplete or oversized report')
    result = {}
    for line in raw.decode('ascii').splitlines():
        key, value = line.split('=', 1)
        if not key or key in result:
            raise ValueError('Duplicate or empty key')
        result[key] = value
    return result


FOREGROUND=(0xff0000,0x00ff00,0xffffff,0xffff00)
BACKGROUND=(0x00ffff,0xff00ff,0x0000ff,0)
def allowed(stage,x,y):
    if x>=12 and y>=12 and 6*x+7*y<=724:return {FOREGROUND[stage]}
    if x<=4 or y<=4 or 6*x+7*y>=828:return {BACKGROUND[stage]}
    return {FOREGROUND[stage],BACKGROUND[stage]}

def pixels(captures):
    sizes={'source':128*112*4,'post':128*112*4,'before':256*192*4,'after':256*192*4}
    if set(captures)!=set(sizes) or any(len(captures[k])!=n*4 for k,n in sizes.items()):raise ValueError('Capture extent')
    if captures['post']!=captures['source']:raise ValueError('Render target changed after presentation')
    for stage in range(4):
        n=sizes['source'];src=struct.unpack('<14336I',captures['source'][stage*n:(stage+1)*n])
        for i,rgb in enumerate(src):
            if rgb not in allowed(stage,i%128,i//128):raise ValueError('D3D source pixel')
        for kind in ('before','after'):
            n=sizes[kind];image=struct.unpack('<49152I',captures[kind][stage*n:(stage+1)*n])
            for i,rgb in enumerate(image):
                x,y=i%256,i//256
                if stage in (1,2) and 48<=x<88 and 40<=y<72:want=0xff00ff
                elif 16<=x<112 and 16<=y<96:want=src[y*128+x] if kind=='after' else 0
                else:want=255
                if rgb!=want:raise ValueError('GDI presentation/guard pixel')
    return sum(len(v) for v in captures.values())

def validate(raw, captures, backend, exit_code):
    r = decode(raw)
    seen = set()
    def need(key, value):
        seen.add(key)
        if r.get(key) != str(value):
            raise ValueError(f'{key}: expected {value}, found {r.get(key)}')
    def integer(key):
        seen.add(key)
        value = r.get(key, '')
        if not value.isascii() or not value.isdigit() or str(int(value)) != value or not 0 <= int(value) <= 0xffffffff:
            raise ValueError(f'Invalid integer: {key}')
        return int(value)
    if backend not in ('default', 'hel') or type(exit_code) is not int or exit_code != 0:
        raise ValueError('Backend/process exit')
    for k, v in dict(schema='xwn-d3d-present-1', rung='08d', backend=backend,
                     visual='UNVERIFIED', scope='rgb-software-window-gdi-readback',
                     result='PRESENTATION_OK', exit=0, end='complete').items():
        need(k, v)
    for k in ('ddraw.load', 'ddraw.entry', 'window.create', 'clipper.owner', 'ddraw.unload'):
        need(k, 1)
    for k in ('ddraw.create', 'ddraw.cooperative', 'ddraw.mode', 'primary.create',
              'primary.format', 'source.create', 'd3d.query', 'enum.hr', 'device.create', 'viewport', 'texture0', 'stage0.op', 'stage0.arg', 'stage0.alpha', 'stage1.op', 'clipper.create', 'clipper.hwnd',
              'clipper.gethwnd', 'primary.clipper', 'primary.detach'):
        need(k, '00000000')
    for k in ('source', 'primary', 'clipper', 'ddraw', 'device'):
        need('release.' + k, 0)
    fmt = tuple(integer('format.' + k) for k in ('flags', 'bits', 'red', 'green', 'blue'))
    if fmt not in ((64, 32, 0xff0000, 0xff00, 255), (64, 16, 0xf800, 0x7e0, 31), (64, 16, 0x7c00, 0x3e0, 31)):
        raise ValueError('Unsupported native format')
    if integer('mode.bpp') != fmt[1] or integer('mode.width') < 640 or integer('mode.height') < 480:
        raise ValueError('Mode/format disagreement')
    for key in ('os.major', 'os.minor', 'os.build'):
        integer(key)
    need('enum.matches',1);need('enum.error',0);need('modules.ok',1)
    if not 1<=integer('enum.count')<=16:raise ValueError('Enumeration capacity')
    seen.add('selected.caps');caps=bytes.fromhex(r.get('selected.caps',''))
    if len(caps)!=236 or caps.hex()!=r['selected.caps']:raise ValueError('Caps extent')
    # Pinned D3DDEVICEDESC7 ABI, independently shared with graphics_discovery.
    if caps[196:212]!=bytes.fromhex('605c66a47326cf11a31a00aa00b93356'):raise ValueError('Not RGB software')
    devcaps=struct.unpack_from('<I',caps,0)[0];depths=struct.unpack_from('<I',caps,116)[0]
    if devcaps&0x90000 or not depths&(0x100 if fmt[1]==32 else 0x400):raise ValueError('Renderer caps')
    for name,value in dict(z=0,zwrite=0,lighting=0,cull=1,fill=3,shade=1,fog=0,alpha=0,alphatest=0,dither=0,specular=0,antialias=0).items():
        need('state.'+name,'00000000');need('get.'+name,'00000000');need('value.'+name,value)
    modules=[]
    count=integer('modules');need('modules.end_error',18)
    if not 1<=count<=64:raise ValueError('Module capacity')
    for i in range(count):
        key=f'module{i}.path';seen.add(key);module_raw=bytes.fromhex(r.get(key,''))
        if not module_raw or len(module_raw)>=260 or 0 in module_raw or module_raw.hex()!=r[key] or not integer(f'module{i}.bytes'):raise ValueError('Module identity')
        name=module_raw.decode('ascii')
        if not name.lower().startswith('c:\\') or '..' in name.split('\\') or '/' in name:raise ValueError('Module path')
        modules.append(name)
    if len({n.lower() for n in modules})!=count:raise ValueError('Duplicate module')
    if not any(n.lower().endswith('\\ddraw.dll') for n in modules):raise ValueError('Missing runtime')
    integer('release.d3d')
    for stage in range(4):
        prefix = f's{stage}.'
        ox, oy = (64, 64) if stage < 2 else (144, 112)
        need(prefix + 'origin.x', ox); need(prefix + 'origin.y', oy)
        need(prefix + 'cover', int(stage in (1, 2)))
        need(prefix + 'cover.visible', int(stage in (1, 2)))
        need(prefix + 'cover.above', 1)
        if integer(prefix + 'cover.preabove') not in (0, 1):
            raise ValueError('Invalid prior sibling order')
        for key in ('clip.size', 'clip.list', 'source.lock', 'post.lock', 'source.unlock', 'post.unlock', 'clear', 'scene.begin', 'draw', 'scene.end', 'primary.blit'):
            need(prefix + key, '00000000')
        for key in ('clip.exact', 'before.capture', 'after.capture', 'source.layout', 'post.layout', 'complete'):
            need(prefix + key, 1)
        need(prefix + 'before.mismatches', 0); need(prefix + 'after.mismatches', 0)
        for key in ('source.pitch', 'post.pitch'):
            pitch = integer(prefix + key)
            if not 128 * (fmt[1] // 8) <= pitch <= 65536 or pitch % (fmt[1] // 8):
                raise ValueError('Invalid pitch')
        for key in ('source.mismatches','post.mismatches'):need(prefix+key,0)
        need(prefix+'foreground',FOREGROUND[stage]);need(prefix+'background',BACKGROUND[stage])
        vertices=b''.join(struct.pack('<ffffI',x,y,.5,1,0xff000000|FOREGROUND[stage]) for x,y in [(8,8),(120,8),(8,104)])
        need(prefix+'vertices',vertices.hex())
        count = integer(prefix + 'clip.count')
        if not 1 <= count <= 64:
            raise ValueError('Clip capacity')
        need(prefix + 'clip.bytes', 32 + count * 16)
        coverage = bytearray(96 * 80)
        for i in range(count):
            left, top, right, bottom = (integer(prefix + f'clip.r{i}.' + k)
                                       for k in ('left', 'top', 'right', 'bottom'))
            left -= ox; right -= ox; top -= oy; bottom -= oy
            if not 16 <= left < right <= 112 or not 16 <= top < bottom <= 96:
                raise ValueError('Clip leaks outside owned target')
            for y in range(top, bottom):
                for x in range(left, right):
                    index = (y-16)*96 + x-16
                    if coverage[index]:
                        raise ValueError('Overlapping clip rectangles')
                    coverage[index] = 1
        for y in range(16, 96):
            for x in range(16, 112):
                want = not (stage in (1, 2) and 48 <= x < 88 and 40 <= y < 72)
                if coverage[(y-16)*96+x-16] != want:
                    raise ValueError('Occlusion/clip coverage mismatch')
    if set(r)!=seen:raise ValueError('Unknown report fields')
    total = pixels(captures)
    return dict(passed=True, backend=backend, stages=4, exact_bytes=total,
                modules=modules, display=[integer('mode.width'), integer('mode.height'), fmt[1]],
                report_sha256=hashlib.sha256(raw).hexdigest(), visual='UNVERIFIED',
                scope='RGB software triangle with bounded edges and exact source-to-GDI mapping; no GPU/scanout/performance claim')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', required=True, choices=('default', 'hel'))
    a = p.parse_args(); prefix = str(a.prefix)
    result = validate(Path(prefix+'.txt').read_bytes(),
                      {k:Path(prefix+'-'+k+'.bin').read_bytes() for k in ('source','before','after','post')},
                      a.backend, int(Path(prefix+'.exit').read_text().strip()))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
