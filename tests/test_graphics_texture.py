# SPDX-License-Identifier: MIT
import struct
import sys
import unittest
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_texture as g


def frames(alpha=False):
    clear=bytearray(struct.pack('<I',g.BG)*4096);draw=bytearray(clear)
    for y in range(8,56):
        for x in range(8,56):struct.pack_into('<I',draw,(y*64+x)*4,g.color((x-8)//6,(y-8)//6))
    source=bytearray(b''.join(struct.pack('<I',g.color(x,y)|(0xff000000 if alpha else 0)) for y in range(8) for x in range(8)))
    return clear,draw,source,bytearray(source)


def record(alpha=False):
    f={k:'0' for k in g.HRESULTS}
    f.update(schema='xwn-d3d-texture-1',backend='default',scope='offscreen-rgb-software',
             width='64',height='64',exit='0',result='CAPTURED',end='complete',modules='1',
             **{'os.major':'5','os.minor':'0','os.build':'2195','window.created':'1',
                'ddraw.load':'1','ddraw.entry':'1','ddraw.unload':'1','enum.matches':'1',
                'enum.error':'0','enum.count':'1','formats.count':'1','formats.selected':'0',
                'formats.error':'0','vertex.stride':'24','vertex.fvf':'260','modules.ok':'1',
                'modules.end_error':'18','release.device':'0','release.texture':'0',
                'release.target':'0','release.ddraw':'0','release.d3d':'1',
                'module0.path':b'C:\\WINNT\\system32\\ddraw.dll'.hex(),'module0.bytes':'4096'})
    caps=bytearray(236);caps[196:212]=uuid.UUID('a4665c60-2673-11cf-a31a-00aa00b93356').bytes_le
    struct.pack_into('<I',caps,116,256);f['device.caps']=caps.hex()
    points=[(8,8,0,0),(56,8,1,0),(8,56,0,1),(8,56,0,1),(56,8,1,0),(56,56,1,1)]
    f['vertices']=b''.join(struct.pack('<6f',x,y,.5,1,u,v) for x,y,u,v in points).hex()
    fmt=struct.pack('<8I',32,65 if alpha else 64,0,32,0xff0000,0xff00,0xff,0xff000000 if alpha else 0).hex()
    f['format0']=fmt
    for s in ('source_before','source_after'):
        f.update({s+'.valid':'1',s+'.pitch':'32',s+'.caps':str(0x1800),s+'.format':fmt})
    for s in ('clear_capture','draw_capture'):
        f.update({s+'.valid':'1',s+'.pitch':'256',s+'.caps':str(0x2840)})
    return f


def encode(f):return ''.join(k+'='+v+'\r\n' for k,v in f.items()).encode()


class TextureTests(unittest.TestCase):
    def test_frames_and_each_pixel(self):
        a,b,c,d=frames();self.assertEqual(g.pixels(a,b,c,d)['interior_pixels'],576)
        for frame in (a,b):
            for at in range(0,len(frame),4):
                frame[at]^=1
                with self.assertRaises(ValueError):g.pixels(a,b,c,d)
                frame[at]^=1
        for frame in (c,d):
            for at in range(len(frame)):
                frame[at]^=1
                with self.assertRaises(ValueError):g.pixels(a,b,c,d)
                frame[at]^=1

    def test_orientation_and_format(self):
        for alpha in (False,True):
            a,b,c,d=frames(alpha);f=record(alpha)
            self.assertTrue(g.validate(encode(f),a,b,c,d,'default',0)['passed'])
            flipped=b''.join(c[y*32:y*32+32] for y in reversed(range(8)))
            with self.assertRaises(ValueError):g.pixels(a,b,flipped,flipped,alpha)
            for i,frame in enumerate((a,b,c,d)):
                bad=[a,b,c,d];bad[i]=frame[:-1]
                with self.assertRaises(ValueError):g.pixels(*bad,alpha)
        a,b,c,d=frames()
        with self.assertRaises(ValueError):g.pixels(a,a,c,d)
        for i in range(3,len(a),4):a[i]=37;b[i]=201
        self.assertTrue(g.pixels(a,b,c,d))

    def test_transport(self):
        f=record();images=frames();raw=encode(f)
        for k in f:
            bad=dict(f);del bad[k]
            for data in (encode(bad),raw+(k+'='+f[k]+'\r\n').encode()):
                with self.assertRaises(ValueError):g.validate(data,*images,'default',0)
        for k in g.HRESULTS:
            bad=dict(f);bad[k]='1'
            with self.assertRaises(ValueError):g.validate(encode(bad),*images,'default',0)
        for k in ('vertices','format0','source_before.format','source_after.format'):
            for i in range(len(bytes.fromhex(f[k]))):
                bad=dict(f);v=bytearray.fromhex(f[k]);v[i]^=1;bad[k]=v.hex()
                with self.assertRaises(ValueError):g.validate(encode(bad),*images,'default',0)
        for k,v in [('formats.selected','1'),('formats.count','65'),('source_before.caps','0'),
                    ('source_after.caps',str(0x401800)),('source_before.pitch','31'),
                    ('source_after.pitch','4097'),('release.texture','1'),('modules','65')]:
            bad=dict(f);bad[k]=v
            with self.assertRaises(ValueError):g.validate(encode(bad),*images,'default',0)


if __name__=='__main__':unittest.main()
