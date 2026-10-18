#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent rational XYZ transform and safe-region RGB oracle for rung09a."""
import argparse
from functools import lru_cache
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import struct
import uuid
from graphics_discovery import integer, unhex
from graphics_d3dpresent import decode

BG, FG = 0x102030, 0x40c080
NAMES = ('identity','world_translate','view_translate','rotate_then_view','perspective','viewport')
STATES = dict(z=0,zwrite=0,lighting=0,cull=1,fill=3,shade=1,fog=0,alpha=0,
              alphatest=0,dither=0,specular=0,antialias=0,clipping=1,colorvertex=1)
BASE_HR = ('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
           'texture0 stage0.op stage0.arg stage0.alpha stage1.op').split()
STAGE_HR = ('clear.viewport clear viewport.set viewport.get world.set world.get view.set '
            'view.get projection.set projection.get scene.begin draw scene.end '
            'clear_capture.lock clear_capture.unlock draw_capture.lock draw_capture.unlock').split()

def identity():
    return [[F(int(i==j)) for j in range(4)] for i in range(4)]

def case(index):
    if type(index) is not int or not 0 <= index < 6:
        raise ValueError('Case index')
    w,v,p=identity(),identity(),identity()
    xyz=[[-F(1,2),F(1,2),F(1,2)],[F(1,2),F(1,2),F(1,2)],[-F(1,2),-F(1,2),F(1,2)]]
    viewport=(0,0,64,64,0,1)
    if index==1:w[3][0]=F(1,4)
    if index==2:v[3][1]=-F(1,4)
    if index==3:
        w[0][0]=w[1][1]=F(0);w[0][1]=F(1);w[1][0]=F(-1);v[3][0]=F(1,4)
    if index==4:
        for q in xyz:q[0]*=2;q[1]*=2
        xyz[0][2]=F(5,4);xyz[1][2]=xyz[2][2]=F(3,2)
        p[2][2]=F(2);p[2][3]=F(1);p[3][2]=F(-2);p[3][3]=F(0)
    if index==5:viewport=(16,16,40,40,0,1)
    return xyz,w,v,p,viewport

def project(xyz,matrices,viewport):
    if len(xyz)!=3 or len(matrices)!=3 or len(viewport)!=6:
        raise ValueError('Transform extent')
    try:
        x,y,width,height,near,far=map(F,viewport)
        if min(x,y)<0 or min(width,height)<=0 or x+width>64 or y+height>64 or not 0<=near<far<=1:
            raise ValueError('Viewport range')
        result=[]
        for vertex in xyz:
            if len(vertex)!=3:raise ValueError('Vertex extent')
            q=list(map(F,vertex))+[F(1)]
            for m in matrices:
                if len(m)!=4 or any(len(row)!=4 for row in m):raise ValueError('Matrix extent')
                q=[sum(q[k]*F(m[k][j]) for k in range(4)) for j in range(4)]
            if q[3]<=0 or not -q[3]<=q[0]<=q[3] or not -q[3]<=q[1]<=q[3] or not 0<=q[2]<=q[3]:
                raise ValueError('Outside this control clip volume')
            result.append((x+(q[0]/q[3]+1)*width/2,y+(1-q[1]/q[3])*height/2))
        if edge(result[0],result[1],result[2])==0:raise ValueError('Degenerate triangle')
        return result
    except (TypeError,ZeroDivisionError,OverflowError) as e:
        raise ValueError('Nonfinite or malformed transform') from e

def edge(a,b,p):return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])

@lru_cache(maxsize=6)
def mask(index):
    xyz,w,v,p,vp=case(index);points=project(xyz,(w,v,p),vp)
    sign=1 if edge(*points)>0 else -1
    result=[]
    for y in range(64):
        for x in range(64):
            distances=[]
            for j in range(3):
                a,b=points[j],points[(j+1)%3]
                # Two pixels in L-infinity distance, fixed before any guest result.
                margin=2*(abs(b[0]-a[0])+abs(b[1]-a[1]))
                distances.append((sign*edge(a,b,(x,y)),margin))
            result.append(1 if all(d>m for d,m in distances) else
                          0 if any(d < -m for d,m in distances) else 2)
    if result.count(1)<20 or result.count(0)<2000:raise ValueError('Insufficient discriminating area')
    return tuple(result)

def pixels(clear,draw):
    if len(clear)!=6*16384 or len(draw)!=6*16384:raise ValueError('Capture extent')
    counts=[]
    for index in range(6):
        c=struct.unpack_from('<4096I',clear,index*16384)
        d=struct.unpack_from('<4096I',draw,index*16384)
        regions=mask(index)
        for j,(a,b,region) in enumerate(zip(c,d,regions)):
            if a&0xffffff!=BG:raise ValueError(f'Clear pixel {index}:{j}')
            allowed=(FG,) if region==1 else (BG,) if region==0 else (BG,FG)
            if b&0xffffff not in allowed:raise ValueError(f'Transformed pixel {index}:{j}')
        counts.append(dict(case=NAMES[index],interior=regions.count(1),exterior=regions.count(0),boundary=regions.count(2)))
    return counts

def geometry_bytes(index):
    xyz,w,v,p,vp=case(index)
    return dict(vertices=b''.join(struct.pack('<fffI',*map(float,q),0xff000000|FG) for q in xyz),
                world=struct.pack('<16f',*[float(n) for row in w for n in row]),
                view=struct.pack('<16f',*[float(n) for row in v for n in row]),
                projection=struct.pack('<16f',*[float(n) for row in p for n in row]),
                viewport=struct.pack('<4I2f',*vp))

def validate(raw,clear,draw,backend,process_exit):
    if backend not in ('default','hel') or type(process_exit) is not int or process_exit!=0:raise ValueError('Backend/exit')
    f=decode(raw);seen=set()
    def need(k,v):
        seen.add(k)
        if f.get(k)!=str(v):raise ValueError('Field mismatch: '+k)
    def num(k):
        seen.add(k);return integer(f.get(k,'?'))
    exact=dict(schema='xwn-d3d-transform-1',backend=backend,scope='offscreen-xyz-transforms-rgb-software',width=64,height=64,stages=6,exit=0,result='CAPTURED',end='complete')
    exact.update({'os.major':5,'os.minor':0,'os.build':2195,'window.created':1,'ddraw.load':1,'ddraw.entry':1,'ddraw.unload':1,'enum.matches':1,'enum.error':0,'vertex.stride':16,'vertex.fvf':66,'modules.ok':1,'modules.end_error':18,'release.device':0,'release.target':0,'release.ddraw':0})
    for k,v in exact.items():need(k,v)
    for k in BASE_HR:need(k,0)
    for k,v in STATES.items():need('state.'+k,0);need('get.state.'+k,0);need('value.state.'+k,v)
    n=num('modules')
    if not 1<=n<=64 or not 1<=num('enum.count')<=16:raise ValueError('Inventory capacity')
    num('release.d3d');seen.add('device.caps');caps=unhex(f.get('device.caps',''),236,236)
    if uuid.UUID(bytes_le=caps[196:212])!=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356'):raise ValueError('RGB identity')
    if struct.unpack_from('<I',caps)[0]&0x90000 or not struct.unpack_from('<I',caps,116)[0]&0x100:raise ValueError('Hardware/format caps')
    for index in range(6):
        prefix=f's{index}.';need(prefix+'name',NAMES[index]);need(prefix+'complete',1)
        for k in STAGE_HR:need(prefix+k,0)
        for k,b in geometry_bytes(index).items():
            need(prefix+k,b.hex())
            if k!='vertices':need(prefix+k+'_readback',b.hex())
        for kind in ('clear_capture','draw_capture'):
            need(prefix+kind+'.valid',1);pitch=num(prefix+kind+'.pitch');c=num(prefix+kind+'.caps')
            if not 256<=pitch<=4096 or pitch%4 or c&0x2840!=0x2840 or c&0x4200:raise ValueError('Surface ownership/pitch')
    modules=[]
    for j in range(n):
        k=f'module{j}.path';seen.add(k);name=unhex(f.get(k,''),1,259).decode('ascii')
        if not name.lower().startswith('c:\\') or '..' in name.split('\\') or '/' in name or not num(f'module{j}.bytes'):raise ValueError('Module identity')
        if name.lower() in [p.lower() for p in modules]:raise ValueError('Duplicate module')
        modules.append(name)
    if not any(p.lower().endswith('\\ddraw.dll') for p in modules):raise ValueError('Missing runtime')
    if seen!=set(f):raise ValueError('Unknown report fields')
    return dict(passed=True,backend=backend,modules=modules,cases=pixels(clear,draw),exact_capture_bytes=len(clear)+len(draw),report_sha256=hashlib.sha256(raw).hexdigest(),scope='Six unlit XYZ matrix/viewport controls; no exact raster edge, clipping, lighting, presentation, GPU or performance qualification')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path);p.add_argument('--backend',choices=['default','hel'],required=True);a=p.parse_args();s=str(a.prefix)
    print(json.dumps(validate(Path(s+'.txt').read_bytes(),Path(s+'-clear.bin').read_bytes(),Path(s+'-draw.bin').read_bytes(),a.backend,int(Path(s+'.exit').read_text())),indent=2))

if __name__=='__main__':main()
