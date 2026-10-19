#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Strict varying-W metadata transport and independent555 perspective oracle."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import uuid
from graphics_discovery import integer, unhex
from graphics_d3dpresent import decode
from graphics_texture import acceptable as texture_acceptable
from graphics_depth import acceptable as depth_acceptable
import graphics_perspective_oracle as oracle

STATES = dict(perspective=1,zfunc=2,z=1,zwrite=1,lighting=0,cull=1,fill=3,shade=1,fog=0,
              alpha=0,alphatest=0,dither=0,specular=0,antialias=0,clipping=1,colorvertex=1)
TEXTURE_STATES = {'stage0.op':2,'stage0.arg':2,'stage0.alpha':1,'stage1.op':1,
                  'stage0.min':1,'stage0.mag':1,'stage0.mip':1,'stage0.u':3,
                  'stage0.v':3,'stage0.coord':0,'stage0.transform':0}
BASE_HR = ('ddraw.create ddraw.cooperative d3d.query enum.hr target.create device.create '
           'zformats.hr tformats.hr depth.create depth.desc depth.attach depth.get_attached '
           'depth.detach texture0.create texture1.create texture.unbind').split()
STAGE_HR = ('clear.viewport clear viewport.set viewport.get world.set world.get view.set '
            'view.get projection.set projection.get scene.begin scene.end state_z.set state_z.get '
            'clear_capture.lock clear_capture.unlock draw_capture.lock draw_capture.unlock '
            'draw0.texture draw0.hr draw1.texture draw1.hr').split()

def geometry_bytes(index):
    g=oracle.geometry(index)
    result={'vertices':b''.join(struct.pack('<5f',*map(float,xyz),*uv)
                              for triangle in g['triangles'] for xyz,uv in zip(triangle,g['uv'])),
            'viewport':struct.pack('<4I2f',*g['viewport'])}
    for name,m in zip(('world','view','projection'),g['matrices']):
        result[name]=struct.pack('<16f',*[float(n) for row in m for n in row])
    return result

def validate(raw,clear,draw,before,after,backend,process_exit):
    if backend not in ('default','hel') or type(process_exit) is not int or process_exit!=0:
        raise ValueError('Backend/exit')
    f=decode(raw);seen=set()
    def need(k,v):
        seen.add(k)
        if f.get(k)!=str(v):raise ValueError('Field mismatch: '+k)
    def num(k):
        seen.add(k);return integer(f.get(k,'?'))
    def blob(k,n):
        seen.add(k);return unhex(f.get(k,''),n,n)
    def ownership(k,minimum,required,forbidden):
        pitch=num(k+'.pitch');caps=num(k+'.caps')
        if not minimum<=pitch<=4096 or pitch%4 or caps&required!=required or caps&forbidden:
            raise ValueError('Surface ownership/pitch: '+k)
        need(k+'.valid',1)
    exact=dict(schema='xwn-d3d-perspective-1',backend=backend,scope='offscreen-xyz-varying-w-software',
               width=64,height=64,stages=5,exit=0,result='CAPTURED',end='complete')
    exact.update({'os.major':5,'os.minor':0,'os.build':2195,'window.created':1,
                  'ddraw.load':1,'ddraw.entry':1,'ddraw.unload':1,'enum.matches':1,'enum.error':0,
                  'vertex.stride':20,'vertex.fvf':258,'modules.ok':1,'modules.end_error':18,
                  'release.device':0,'release.texture0':0,'release.texture1':0,'release.depth':0,
                  'release.target':0,'release.ddraw':0,'depth.identity':1,'depth.width':64,'depth.height':64})
    for k,v in exact.items():need(k,v)
    for k in BASE_HR:need(k,0)
    for k,v in {**{'state.'+k:v for k,v in STATES.items()},**TEXTURE_STATES}.items():
        need(k,0);need('get.'+k,0);need('value.'+k,v)
    n=num('modules')
    if not 1<=n<=64 or not 1<=num('enum.count')<=16:raise ValueError('Inventory capacity')
    num('release.d3d');caps=blob('device.caps',236)
    if uuid.UUID(bytes_le=caps[196:212])!=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356'):
        raise ValueError('RGB identity')
    if struct.unpack_from('<I',caps)[0]&0x90000 or not struct.unpack_from('<I',caps,116)[0]&0x100:
        raise ValueError('Hardware/format caps')
    chosen={}
    for label,accept in [('z',depth_acceptable),('t',texture_acceptable)]:
        count=num(label+'formats.count');index=num(label+'formats.selected');need(label+'formats.error',0)
        if not 1<=count<=64 or not 0<=index<count:raise ValueError('Format capacity/selection')
        formats=[blob(f'{label}format{i}',32) for i in range(count)]
        if any(struct.unpack_from('<I',b)[0]!=32 for b in formats):raise ValueError('Format size')
        possible=[i for i,b in enumerate(formats) if accept(b)]
        if not possible or possible[0]!=index:raise ValueError('First compatible format')
        chosen[label]=formats[index]
    if blob('depth.format',32)!=chosen['z']:raise ValueError('Depth format provenance')
    c=num('depth.caps')
    if c&0x20800!=0x20800 or c&0x4200 or num('depth.release_query')<1:raise ValueError('Depth ownership')
    for i in range(2):
        for when in ('before','after'):
            p=f'source{i}.{when}';need(p+'.lock',0);need(p+'.unlock',0)
            ownership(p,32,0x1800,0x404200)
            if blob(p+'.format',32)!=chosen['t']:raise ValueError('Texture format provenance')
    for i in range(5):
        p=f's{i}.';g=oracle.geometry(i)
        need(p+'name',oracle.NAMES[i]);need(p+'complete',1)
        need(p+'z_enabled',int(g['z_enabled']));need(p+'clear_z',g['clear_z'])
        for j,index in enumerate(g['order']):need(p+f'draw{j}.index',index)
        for k in STAGE_HR:need(p+k,0)
        for k,b in geometry_bytes(i).items():
            need(p+k,b.hex())
            if k!='vertices':need(p+k+'_readback',b.hex())
        for kind in ('clear_capture','draw_capture'):ownership(p+kind,256,0x2840,0x4200)
    modules=[]
    for i in range(n):
        k=f'module{i}.path';seen.add(k);name=unhex(f.get(k,''),1,259).decode('ascii')
        if not name.lower().startswith('c:\\') or '..' in name.split('\\') or '/' in name or not num(f'module{i}.bytes'):
            raise ValueError('Module identity')
        if name.lower() in [p.lower() for p in modules]:raise ValueError('Duplicate module')
        modules.append(name)
    if not any(p.lower().endswith('\\ddraw.dll') for p in modules):raise ValueError('Missing runtime')
    if seen!=set(f):raise ValueError('Unknown report fields')
    alpha=bool(struct.unpack('<8I',chosen['t'])[1]&1)
    checks=oracle.validate(clear,draw,before,after,alpha)
    return dict(passed=True,backend=backend,modules=modules,pixel_checks=checks,
                texture_format=struct.unpack('<8I',chosen['t']),depth_format=struct.unpack('<8I',chosen['z']),
                exact_capture_bytes=len(clear)+len(draw),source_capture_bytes=len(before)+len(after),
                report_sha256=hashlib.sha256(raw).hexdigest(),
                scope='Five offscreen varying-W texture controls; fixed two-pixel bands; high X byte and pitch padding excluded. No presentation, GPU, games or performance qualification.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('prefix',type=Path)
    p.add_argument('--backend',choices=['default','hel'],required=True);a=p.parse_args();s=str(a.prefix)
    print(json.dumps(validate(Path(s+'.txt').read_bytes(),*[Path(s+'-'+n+'.bin').read_bytes()
          for n in ('clear','draw','source-before','source-after')],a.backend,int(Path(s+'.exit').read_text())),indent=2))

if __name__=='__main__':main()
