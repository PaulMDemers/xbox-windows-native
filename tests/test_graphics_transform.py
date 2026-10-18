# SPDX-License-Identifier: MIT
from fractions import Fraction as F
import math
from pathlib import Path
import struct
import sys
import unittest
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_transform as g

def frames():
    clear=struct.pack('<I',g.BG)*(4096*6);draw=bytearray(clear)
    for i in range(6):
        for j,region in enumerate(g.mask(i)):
            if region==1:struct.pack_into('<I',draw,i*16384+j*4,g.FG)
    return clear,draw

def report():
    d=dict(schema='xwn-d3d-transform-1',backend='default',scope='offscreen-xyz-transforms-rgb-software',width=64,height=64,stages=6,exit=0,result='CAPTURED')
    d.update({'os.major':5,'os.minor':0,'os.build':2195,'window.created':1,'ddraw.load':1,'ddraw.entry':1,'ddraw.unload':1,'enum.count':1,'enum.matches':1,'enum.error':0,'vertex.stride':16,'vertex.fvf':66,'modules.ok':1,'modules.end_error':18,'release.device':0,'release.target':0,'release.ddraw':0,'release.d3d':0,'modules':2})
    for k in g.BASE_HR:d[k]=0
    for k,v in g.STATES.items():d['state.'+k]=0;d['get.state.'+k]=0;d['value.state.'+k]=v
    caps=bytearray(236);struct.pack_into('<I',caps,116,0x100);caps[196:212]=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356').bytes_le;d['device.caps']=caps.hex()
    for i in range(6):
        p=f's{i}.';d[p+'name']=g.NAMES[i];d[p+'complete']=1
        for k in g.STAGE_HR:d[p+k]=0
        for k,v in g.geometry_bytes(i).items():
            d[p+k]=v.hex()
            if k!='vertices':d[p+k+'_readback']=v.hex()
        for k in ('clear_capture','draw_capture'):d[p+k+'.valid']=1;d[p+k+'.pitch']=256;d[p+k+'.caps']=0x2840
    for i,path in enumerate([r'C:\owned\transform.exe',r'C:\WINNT\system32\ddraw.dll']):d[f'module{i}.path']=path.encode().hex();d[f'module{i}.bytes']=4096
    d['end']='complete';return {k:str(v) for k,v in d.items()}

def encode(d):return ''.join(k+'='+str(v)+'\r\n' for k,v in d.items()).encode()

class TransformTests(unittest.TestCase):
    def test_known_projected_coordinates(self):
        expected=[[(16,16),(48,16),(16,48)],[(24,16),(56,16),(24,48)],[(16,24),(48,24),(16,56)],[(24,48),(24,16),(56,48)],[(F(32,5),F(32,5)),(F(160,3),F(32,3)),(F(32,3),F(160,3))],[(26,26),(46,26),(26,46)]]
        for i,want in enumerate(expected):
            xyz,w,v,p,vp=g.case(i);self.assertEqual(g.project(xyz,(w,v,p),vp),want)
        xyz,w,v,p,vp=g.case(3);self.assertNotEqual(g.project(xyz,(v,w,p),vp),expected[3])

    def test_invalid_geometry(self):
        xyz,w,v,p,vp=g.case(0)
        for bad in [[],[[1]],[[math.inf]*4]*4,[[math.nan]*4]*4,[[0]*4]*4]:
            with self.assertRaises(ValueError):g.project(xyz,(w,v,bad),vp)
        for bad in [(0,0,0,64,0,1),(-1,0,64,64,0,1),(0,0,65,64,0,1),(0,0,64,64,1,0)]:
            with self.assertRaises(ValueError):g.project(xyz,(w,v,p),bad)
        for vertices in [[(2,0,.5)]*3,[(0,0,-1)]*3,[(0,0,2)]*3,[(0,0,.5)]*3]:
            with self.assertRaises(ValueError):g.project(vertices,(w,v,p),vp)

    def test_pixels_and_discriminators(self):
        clear,draw=frames();self.assertEqual(len(g.pixels(clear,draw)),6)
        for i in range(6):
            for region in (0,1,2):
                j=g.mask(i).index(region);bad=bytearray(draw);struct.pack_into('<I',bad,i*16384+j*4,0x123456)
                with self.assertRaises(ValueError):g.pixels(clear,bad)
            missing=bytearray(draw);missing[i*16384:(i+1)*16384]=clear[i*16384:(i+1)*16384]
            with self.assertRaises(ValueError):g.pixels(clear,missing)
            if i:
                unchanged=bytearray(draw);unchanged[i*16384:(i+1)*16384]=draw[:16384]
                with self.assertRaises(ValueError):g.pixels(clear,unchanged)
        for a,b in [(clear[:-1],draw),(clear,draw+b'\0')]:
            with self.assertRaises(ValueError):g.pixels(a,b)

    def test_transport_every_field(self):
        clear,draw=frames();d=report();raw=encode(d);self.assertTrue(g.validate(raw,clear,draw,'default',0)['passed'])
        import hashlib
        self.assertEqual(g.validate(raw,clear,draw,'default',0)['report_sha256'],hashlib.sha256(raw).hexdigest())
        for k in d:
            for remove in (False,True):
                bad=dict(d)
                if remove:del bad[k]
                else:bad[k]='invalid'
                with self.assertRaises((ValueError,UnicodeError),msg=k):g.validate(encode(bad),clear,draw,'default',0)
        bad=dict(d);bad['s0.world_readback']=g.geometry_bytes(1)['world'].hex()
        with self.assertRaises(ValueError):g.validate(encode(bad),clear,draw,'default',0)
        for code in (1,True):
            with self.assertRaises(ValueError):g.validate(raw,clear,draw,'default',code)

if __name__=='__main__':unittest.main()
