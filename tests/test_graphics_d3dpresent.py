# SPDX-License-Identifier: MIT
"""Independent synthetic geometry and refusal controls, not a guest result."""
import struct
import hashlib
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from test_graphics_present import fixture as old_fixture,encode
import graphics_d3dpresent as g


def fixture():
    r,_=old_fixture()
    r.update(schema='xwn-d3d-present-1',rung='08d',scope='rgb-software-window-gdi-readback')
    r.pop('end')
    for k in ('d3d.query','enum.hr','device.create','viewport','texture0','stage0.op','stage0.arg','stage0.alpha','stage1.op'):
        r[k]='00000000'
    r.update({'enum.count':1,'enum.matches':1,'enum.error':0,'modules.ok':1,
              'modules':2,'modules.end_error':18,'release.device':0,'release.d3d':1})
    caps=bytearray(236);caps[196:212]=bytes.fromhex('605c66a47326cf11a31a00aa00b93356');struct.pack_into('<I',caps,116,0x500)
    r['selected.caps']=caps.hex()
    for n,v in dict(z=0,zwrite=0,lighting=0,cull=1,fill=3,shade=1,fog=0,alpha=0,alphatest=0,dither=0,specular=0,antialias=0).items():
        r['state.'+n]=r['get.'+n]='00000000';r['value.'+n]=v
    for i,path in enumerate([r'C:\xwn491\d3d.exe',r'C:\WINNT\system32\ddraw.dll']):
        r[f'module{i}.path']=path.encode().hex();r[f'module{i}.bytes']=65536
    captures={k:bytearray() for k in ('source','post','before','after')}
    fg=[0xff0000,0x00ff00,0xffffff,0xffff00];bg=[0x00ffff,0xff00ff,0x0000ff,0]
    for s in range(4):
        p=f's{s}.'
        for k in ('source.write.lock','source.read.lock','source.write.unlock','source.read.unlock','source.write.layout','source.read.layout','source.exact','source.write.pitch','source.read.pitch'):del r[p+k]
        for k in ('source.lock','post.lock','source.unlock','post.unlock','clear','scene.begin','draw','scene.end'):r[p+k]='00000000'
        for k in ('source.layout','post.layout'):r[p+k]=1
        for k in ('source.pitch','post.pitch'):r[p+k]=512
        for k in ('source.mismatches','post.mismatches'):r[p+k]=0
        r[p+'foreground']=fg[s];r[p+'background']=bg[s]
        r[p+'vertices']=b''.join(struct.pack('<ffffI',x,y,.5,1,0xff000000|fg[s]) for x,y in [(8,8),(120,8),(8,104)]).hex()
        # Construct one synthetic rasterization without consulting the validator.
        src=[fg[s] if x>=8 and y>=8 and 6*x+7*y<776 else bg[s] for y in range(112) for x in range(128)]
        b=struct.pack('<14336I',*src);captures['source']+=b;captures['post']+=b
        for kind in ('before','after'):
            for y in range(192):
                for x in range(256):
                    if s in (1,2) and 48<=x<88 and 40<=y<72:v=0xff00ff
                    elif 16<=x<112 and 16<=y<96:v=src[y*128+x] if kind=='after' else 0
                    else:v=255
                    captures[kind]+=struct.pack('<I',v)
    r['end']='complete'
    return r,{k:bytes(v) for k,v in captures.items()}


class D3DPresentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r,cls.c=fixture()
    def test_positive_native_formats(self):
        for bits,red,green,blue in [(32,0xff0000,0xff00,255),(16,0xf800,0x7e0,31),(16,0x7c00,0x3e0,31)]:
            r=dict(self.r);r.update({'format.bits':bits,'format.red':red,'format.green':green,'format.blue':blue,'mode.bpp':bits})
            self.assertEqual(g.validate(encode(r),self.c,'default',0)['exact_bytes'],2031616)
    def test_missing_mutated_unknown_fields(self):
        for key in self.r:
            for remove in (False,True):
                r=dict(self.r)
                if remove:del r[key]
                else:r[key]='invalid'
                with self.subTest(key=key,remove=remove),self.assertRaises(ValueError):g.validate(encode(r),self.c,'default',0)
        r=dict(self.r);r['unclaimed']='0'
        with self.assertRaises(ValueError):g.validate(encode(r),self.c,'default',0)
    def test_pixels_lifetimes_and_guards(self):
        for kind in self.c:
            for off in (0,4*(20*128+20),len(self.c[kind])//2,len(self.c[kind])-1):
                c=dict(self.c);b=bytearray(c[kind]);b[off]^=1;c[kind]=bytes(b)
                with self.subTest(kind=kind,off=off),self.assertRaises(ValueError):g.pixels(c)
            c=dict(self.c);c[kind]=c[kind][:-1]
            with self.assertRaises(ValueError):g.pixels(c)
        c=dict(self.c);c['post']=c['source'][57344:]+c['source'][:57344]
        with self.assertRaises(ValueError):g.pixels(c)
        c=dict(self.c);c['after']=c['before']
        with self.assertRaises(ValueError):g.pixels(c)
    def test_backend_exit_caps_transport(self):
        for backend,code in [('hal',0),('hel',0),('default',1),('default',False)]:
            with self.assertRaises(ValueError):g.validate(encode(self.r),self.c,backend,code)
        for off,mask in [(196,1),(2,1),(2,8),(117,1)]:
            r=dict(self.r);b=bytearray.fromhex(r['selected.caps']);b[off]^=mask;r['selected.caps']=b.hex()
            with self.assertRaises(ValueError):g.validate(encode(r),self.c,'default',0)
        for raw in [encode(self.r)[:-2],b'exit=0\r\n'+encode(self.r)]:
            with self.assertRaises(ValueError):g.validate(raw,self.c,'default',0)
    def test_actual_report_digest(self):
        r=g.validate(encode(self.r),self.c,'default',0)
        self.assertEqual(r['report_sha256'],hashlib.sha256(encode(self.r)).hexdigest())
    def test_edge_allowance_is_bounded(self):
        self.assertEqual(g.allowed(0,8,8),{0xff0000,0x00ffff})
        self.assertEqual(g.allowed(0,20,20),{0xff0000})
        self.assertEqual(g.allowed(0,127,111),{0x00ffff})


if __name__=='__main__':unittest.main()
