#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent RGB32 key-probe reader. Unexpected pixels remain failures."""
import argparse
import json
from pathlib import Path
import struct

COLORS = (0, 0xff0000, 0x010000, 1, 0x00ff00, 0x123456, 0xab3456, 0x123457,
          0x120000, 0xffffff, 0x00ffff, 0xff00ff, 0x654321, 0x124321, 255, 0x010001)
KEYS = (0, 0xff0000, 0x123456)
SOURCE = tuple(COLORS[(x+3*y) % 16] for y in range(12) for x in range(16))


def expected(stage):
    if type(stage) is not int or not 0 <= stage < 12:
        raise ValueError('Stage range')
    result = [0x335577] * (32*24)
    keyed, clipped, key = stage % 2, (stage//2) % 2, KEYS[stage//4]
    for sy in range(12):
        for sx in range(16):
            x, y = sx+4, sy+4
            visible = not clipped or (5 <= y < 15 and (6 <= x < 12 or 14 <= x < 19))
            value = SOURCE[sy*16+sx]
            if visible and (not keyed or value != key):
                result[y*32+x] = value
    return tuple(result)


def decode(raw):
    if not 0 < len(raw) <= 1024*1024:
        raise ValueError('Report size')
    fields = {}
    for line in raw.decode('ascii').splitlines():
        k, v = line.split('=')
        if not k or k in fields or not v:
            raise ValueError('Duplicate/empty field')
        fields[k] = v
    return fields


def validate(raw, source, dest, backend, process_exit):
    f = decode(raw)
    used = set()
    def exact(k, value):
        used.add(k)
        if f.get(k) != str(value):
            raise ValueError('Field mismatch: '+k)
    def integer(k, low, high):
        used.add(k)
        v = f.get(k, '')
        if not v.isascii() or not v.isdecimal() or str(int(v)) != v or not low <= int(v) <= high:
            raise ValueError('Integer range: '+k)
        return int(v)
    if backend not in ('default', 'hel') or type(process_exit) is not int:
        raise ValueError('Caller metadata')
    for k,v in {'schema':'xwn-keyprobe-1','backend':backend,'scope':'owned-rgb32-system-memory',
                'os.major':5,'os.minor':0,'os.build':2195,'modes.complete':1,
                'window.create':1,'ddraw.load':1,'ddraw.entry':1,'clipper.exact':1,
                'cleanup.clipper.attached':1,'ddraw.unload':1,'completed':12,'end':'complete'}.items():exact(k,v)
    for k in ('ddraw.create','ddraw.cooperative','ddraw.mode','source.create','dest.create',
              'clipper.create','clipper.set','clipper.get','cleanup.clipper'):exact(k,'00000000')
    for k in ('dest','source','clipper','ddraw'):exact('release.'+k,0)
    width=integer('desktop.width',640,8192);height=integer('desktop.height',480,8192)
    bpp=integer('desktop.bpp',8,32)
    if bpp not in (8,16,24,32):raise ValueError('Desktop depth')
    for k,v in [('width',width),('height',height),('bpp',bpp)]:exact('mode.'+k,v)
    mode_count=integer('modes.count',1,4095)
    modes=[]
    for i in range(mode_count):
        row={k:integer(f'm{i}.{k}',lo,hi) for k,lo,hi in
             [('width',1,8192),('height',1,8192),('bpp',1,32),('hz',0,1000),('flags',0,0xffffffff)]}
        modes.append(row)
    if len(source)!=12*16*12*4 or len(dest)!=12*32*24*4:raise ValueError('Capture length')
    src=struct.unpack('<2304I',source);dst=struct.unpack('<9216I',dest)
    rows=[];total=0
    for stage in range(12):
        pre=f's{stage}.'
        for k,v in [('key.requested',KEYS[stage//4]),('key.low',KEYS[stage//4]),
                    ('key.high',KEYS[stage//4]),('keyed',stage%2),('clipped',(stage//2)%2),('complete',1)]:exact(pre+k,v)
        for k in ('key.set','key.get','blit'):exact(pre+k,'00000000')
        if stage in (2,4,6,8,10):exact(pre+'clipper.change','00000000')
        accesses=['dest.write','source.read','dest.read']+(['source.write'] if stage==0 else [])
        for label in accesses:
            exact(pre+label+'.lock','00000000');exact(pre+label+'.unlock','00000000');exact(pre+label+'.layout',1)
            pitch=integer(pre+label+'.pitch',64 if label.startswith('source') else 128,65536)
            if pitch%4:raise ValueError('Pitch alignment')
        actual_source=src[stage*192:(stage+1)*192]
        actual_dest=dst[stage*768:(stage+1)*768]
        source_bad=sum(a!=b for a,b in zip(actual_source,SOURCE))
        bad=sum(a!=b for a,b in zip(actual_dest,expected(stage)))
        exact(pre+'source.read.mismatches',source_bad);exact(pre+'dest.read.mismatches',bad)
        total+=source_bad+bad
        rows.append(dict(stage=stage,key=KEYS[stage//4],keyed=bool(stage%2),clipped=bool((stage//2)%2),
                         source_mismatches=source_bad,dest_mismatches=bad,passed=source_bad+bad==0))
    exact('mismatches',total);code=1 if total else 0
    exact('exit',code);exact('result','FAILED' if total else 'KEYPROBE_OK')
    if process_exit!=code:raise ValueError('Process/receipt exit mismatch')
    if set(f)!=used:raise ValueError('Unrecognized fields: '+repr(sorted(set(f)-used)))
    return dict(complete_observation=True,semantics_passed=total==0,rows=rows,modes=modes,
                desktop=dict(width=width,height=height,bpp=bpp),mismatches=total,
                captured_bytes=len(source)+len(dest),scope='NT5 RGB32 system-memory diagnostic; no scanout/GPU claim')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix',type=Path);p.add_argument('--backend',required=True,choices=('default','hel'))
    a=p.parse_args();base=str(a.prefix)
    result=validate(Path(base+'.txt').read_bytes(),Path(base+'-source.bin').read_bytes(),
                    Path(base+'-dest.bin').read_bytes(),a.backend,int(Path(base+'.exit').read_text().strip()))
    print(json.dumps(result,indent=2))
    return 0 if result['semantics_passed'] else 1


if __name__=='__main__':raise SystemExit(main())
