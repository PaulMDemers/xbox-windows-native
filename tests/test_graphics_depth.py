# SPDX-License-Identifier: MIT
import struct
import sys
import unittest
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_depth as g


def frames():
    result=[]
    for color in (g.BG,g.FG,g.FG,g.FAR,g.BG):
        f=bytearray(struct.pack('<I',g.BG)*4096)
        for y in range(8,56):
            for x in range(8,64-y):struct.pack_into('<I',f,(y*64+x)*4,color)
        result.append(f)
    return result


def record():
    f={k:'0' for k in g.HRESULTS}
    f.update(schema='xwn-d3d-depth-1',backend='default',scope='offscreen-rgb-software',
             width='64',height='64',exit='0',result='CAPTURED',end='complete',modules='1',
             **{'os.major':'5','os.minor':'0','os.build':'2195','window.created':'1',
                'ddraw.load':'1','ddraw.entry':'1','ddraw.unload':'1','enum.matches':'1',
                'enum.error':'0','enum.count':'1','formats.count':'1','formats.selected':'0',
                'formats.error':'0','vertex.stride':'20','vertex.fvf':'68','modules.ok':'1',
                'modules.end_error':'18','release.device':'0','release.depth':'0',
                'release.target':'0','release.ddraw':'0','release.d3d':'1',
                'depth.width':'64','depth.height':'64','depth.identity':'1',
                'depth.caps':str(0x20800),'depth.release_query':'2',
                'module0.path':b'C:\\WINNT\\system32\\ddraw.dll'.hex(),'module0.bytes':'4096'})
    caps=bytearray(236);caps[196:212]=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356').bytes_le
    struct.pack_into('<I',caps,116,256);f['device.caps']=caps.hex()
    f['vertices']=b''.join(struct.pack('<ffffI',x,y,z,1,c) for z,c in [(.25,0xff40c080),(.75,0xffc04080)] for x,y in [(8,8),(56,8),(8,56)]).hex()
    f['format0']=f['depth.format']=struct.pack('<8I',32,0x400,0,16,0,65535,0,0).hex()
    for i,s in enumerate(g.STAGES):
        f.update({s+'.valid':'1',s+'.pitch':'256',s+'.caps':str(0x2840),s+'.z_enabled':'0' if i==3 else '1',s+'.clear_z':'0' if i==4 else '1'})
        if i:f.update({s+'.draw0.index':'1' if i==1 else '0',s+'.draw1.index':'0' if i==1 else '1'})
    return f


def encode(f):return ''.join(k+'='+v+'\r\n' for k,v in f.items()).encode()


class DepthTests(unittest.TestCase):
    def test_every_rgb_pixel(self):
        images=frames();self.assertEqual(g.pixels(*images)['far_near']['interior_pixels'],561)
        for frame in images:
            for at in range(0,len(frame),4):
                frame[at]^=1
                with self.assertRaises(ValueError):g.pixels(*images)
                frame[at]^=1

    def test_depth_discriminators(self):
        images=frames();self.assertTrue(g.validate(encode(record()),images,'default',0)['passed'])
        # Painter's order, missing Z writes, missing clear and ignored disable.
        for dest,source in [(2,3),(1,3),(1,0),(3,1),(4,1),(4,3)]:
            bad=list(images);bad[dest]=images[source]
            with self.assertRaises(ValueError):g.pixels(*bad)
        for i in range(5):
            bad=list(images);bad[i]=bad[i][:-1]
            with self.assertRaises(ValueError):g.pixels(*bad)
        for frame in images:
            for at in range(3,len(frame),4):frame[at]=123
        self.assertTrue(g.pixels(*images))

    def test_transport(self):
        f=record();images=frames();raw=encode(f)
        for k in f:
            bad=dict(f);del bad[k]
            for data in (encode(bad),raw+(k+'='+f[k]+'\r\n').encode()):
                with self.assertRaises(ValueError):g.validate(data,images,'default',0)
        for k in g.HRESULTS:
            bad=dict(f);bad[k]='1'
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)
        for i in range(120):
            bad=dict(f);v=bytearray.fromhex(f['vertices']);v[i]^=1;bad['vertices']=v.hex()
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)
        for k,v in [('formats.selected','1'),('formats.count','65'),('depth.caps','0'),('depth.identity','0'),
                    ('depth.width','63'),('depth.release_query','0'),('release.depth','1'),('modules','65'),
                    ('near_far.draw0.index','1'),('zero_z.clear_z','1'),('no_z.z_enabled','1')]:
            bad=dict(f);bad[k]=v
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)
        for index,value in [(0,31),(1,0),(2,1),(3,8),(4,8),(6,255)]:
            bad=dict(f);v=list(struct.unpack('<8I',bytes.fromhex(f['format0'])));v[index]=value
            bad['format0']=bad['depth.format']=struct.pack('<8I',*v).hex()
            with self.assertRaises(ValueError):g.validate(encode(bad),images,'default',0)


if __name__=='__main__':unittest.main()
