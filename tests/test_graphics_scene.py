# SPDX-License-Identifier: MIT
"""Synthetic transport tests; API/COM/device values are models, not guest evidence."""
from pathlib import Path
import struct
import sys
import unittest
import uuid
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_scene as g

def frames():
    clear=struct.pack('<I',g.oracle.BG)*(4096*5)
    draw=b''.join(struct.pack('<I',min(allowed)) for i in range(5) for allowed,_ in g.oracle.pixels_for_stage(i))
    return clear,draw,g.oracle.sources(False),g.oracle.sources(False)

def report():
    d=dict(schema='xwn-d3d-scene-1',backend='default',scope='offscreen-xyz-texture-depth-rgb-software',width=64,height=64,stages=5,exit=0,result='CAPTURED')
    d.update({'os.major':5,'os.minor':0,'os.build':2195,'window.created':1,'ddraw.load':1,'ddraw.entry':1,'ddraw.unload':1,'enum.count':1,'enum.matches':1,'enum.error':0,'vertex.stride':20,'vertex.fvf':258,'modules.ok':1,'modules.end_error':18,'release.device':0,'release.target':0,'release.ddraw':0,'release.d3d':0,'release.texture0':0,'release.texture1':0,'release.depth':0,'modules':2,'depth.identity':1,'depth.width':64,'depth.height':64,'depth.caps':0x20800,'depth.release_query':2})
    for k in g.BASE_HR:d[k]=0
    for k,v in {**{'state.'+k:v for k,v in g.STATES.items()},**g.TEXTURE_STATES}.items():
        d[k]=0;d['get.'+k]=0;d['value.'+k]=v
    caps=bytearray(236);struct.pack_into('<I',caps,116,0x100);caps[196:212]=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356').bytes_le;d['device.caps']=caps.hex()
    tf=struct.pack('<8I',32,64,0,32,0xff0000,0xff00,0xff,0).hex()
    zf=struct.pack('<8I',32,0x400,0,16,0,0xffff,0,0).hex()
    for label,fmt in [('t',tf),('z',zf)]:
        d[label+'formats.count']=1;d[label+'formats.selected']=0;d[label+'formats.error']=0;d[label+'format0']=fmt
    d['depth.format']=zf
    for i in range(2):
        for when in ('before','after'):
            p=f'source{i}.{when}';d[p+'.lock']=0;d[p+'.unlock']=0;d[p+'.valid']=1;d[p+'.pitch']=32;d[p+'.caps']=0x1800;d[p+'.format']=tf
    for i in range(5):
        p=f's{i}.';d[p+'name']=g.oracle.NAMES[i];d[p+'complete']=1
        d[p+'z_enabled']=int(i!=2);d[p+'clear_z']=int(i!=3)
        for j,v in enumerate((1,0) if i==0 else (0,1)):d[p+f'draw{j}.index']=v
        for k in g.STAGE_HR:d[p+k]=0
        for k,v in g.geometry_bytes(i).items():
            d[p+k]=v.hex()
            if k!='vertices':d[p+k+'_readback']=v.hex()
        for kind in ('clear_capture','draw_capture'):
            d[p+kind+'.valid']=1;d[p+kind+'.pitch']=256;d[p+kind+'.caps']=0x2840
    for i,path in enumerate([r'C:\owned\scene.exe',r'C:\WINNT\system32\ddraw.dll']):
        d[f'module{i}.path']=path.encode().hex();d[f'module{i}.bytes']=4096
    d['end']='complete';return {k:str(v) for k,v in d.items()}

def encode(d):return ''.join(k+'='+str(v)+'\r\n' for k,v in d.items()).encode()

class SceneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=frames();cls.d=report()
    def verify(self,d=None,data=None,backend='default',code=0):
        return g.validate(encode(self.d if d is None else d),*(self.data if data is None else data),backend,code)
    def test_positive(self):
        self.assertTrue(self.verify()['passed'])
        d=dict(self.d);d['backend']='hel';self.assertTrue(self.verify(d,backend='hel')['passed'])
        d=dict(self.d);tf=struct.pack('<8I',32,65,0,32,0xff0000,0xff00,0xff,0xff000000).hex()
        for k in d:
            if k=='tformat0' or (k.startswith('source') and k.endswith('.format')):d[k]=tf
        self.assertTrue(self.verify(d,(*self.data[:2],g.oracle.sources(True),g.oracle.sources(True)))['passed'])
    def test_every_field(self):
        for k in self.d:
            for remove in (False,True):
                d=dict(self.d)
                if remove:del d[k]
                else:d[k]='invalid'
                with self.assertRaises(ValueError,msg=k):self.verify(d)
    def test_semantic_negatives(self):
        for k,v in [('tformats.count',65),('zformats.selected',1),('depth.identity',0),('depth.caps',0x24800),('depth.release_query',0),('source0.before.caps',0x401800),('source1.after.pitch',33),('s2.z_enabled',1),('s0.draw0.index',0),('s4.world_readback',self.d['s0.world']),('s0.viewport_readback',self.d['s1.vertices']),('modules',0),('module1.path',self.d['module0.path']),('module1.bytes',0),('value.stage0.min',2),('value.state.zwrite',0),('s0.clear_capture.pitch',257),('release.texture1',1)]:
            d=dict(self.d);d[k]=v
            with self.assertRaises(ValueError,msg=k):self.verify(d)
        for label in ('t','z'):
            d=dict(self.d);d[label+'formats.count']=2;d[label+'formats.selected']=1;d[label+'format1']=d[label+'format0']
            with self.assertRaises(ValueError):self.verify(d)
        for offset in (0,116,196):
            d=dict(self.d);b=bytearray.fromhex(d['device.caps'])
            if offset==0:struct.pack_into('<I',b,0,0x90000)
            elif offset==116:struct.pack_into('<I',b,116,0)
            else:b[offset]^=0xff
            d['device.caps']=b.hex()
            with self.assertRaises(ValueError):self.verify(d)
    def test_transport_and_extent(self):
        raw=encode(self.d)
        for bad in (raw[:-1],b'width=64\r\n'+raw,b'unknown=1\r\n'+raw,b'x'*65537+raw,b'\xff'+raw):
            with self.assertRaises(ValueError):g.validate(bad,*self.data,'default',0)
        for i in range(4):
            for diff in (-1,1):
                data=list(self.data);data[i]=data[i][:-1] if diff<0 else data[i]+b'\0'
                with self.assertRaises(ValueError):self.verify(data=data)
        for code in (1,True,-1):
            with self.assertRaises(ValueError):self.verify(code=code)
    def test_pixel_and_source_join(self):
        for stage in range(5):
            for stream in (0,1):
                data=list(self.data);b=bytearray(data[stream]);struct.pack_into('<I',b,stage*16384,0x123456);data[stream]=b
                with self.assertRaises(ValueError):self.verify(data=data)
        for stream in (2,3):
            for offset in (0,255,256,511):
                data=list(self.data);b=bytearray(data[stream]);b[offset]^=1;data[stream]=b
                with self.assertRaises(ValueError):self.verify(data=data)
        for stage in (0,1,2,4):
            data=list(self.data);b=bytearray(data[1]);b[stage*16384:(stage+1)*16384]=data[0][:16384];data[1]=b
            with self.assertRaises(ValueError):self.verify(data=data)

if __name__=='__main__':unittest.main()
