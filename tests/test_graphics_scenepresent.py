# SPDX-License-Identifier: MIT
"""Synthetic transport/geometry controls, not device evidence."""
import struct
import unittest
import test_graphics_scene as base
import graphics_scenepresent as g

def fixture(bits=16,red=0xf800):
    d=base.report();data=list(base.frames());pixels=struct.unpack('<20480I',data[1])
    d.update(schema='xwn-scene-present-2',scope='windowed-xyz-texture-depth-rgb-software')
    for k in ('mode','primary.create','primary.format','clipper.create','clipper.hwnd','clipper.gethwnd',
              'primary.clipper','primary.detach','release.primary','release.clipper','bridge.create','release.bridge'):d['p.'+k]=0
    d.update({'p.clipper.owner':1,'p.mode.bits':bits,'p.mode.width':640,'p.mode.height':480,
              'p.format':struct.pack('<8I',32,64,0,bits,0xff0000 if bits==32 else red,0xff00 if bits==32 else 0x7e0 if red==0xf800 else 0x3e0,255 if bits==32 else 31,0).hex()})
    def packed(v):
        if bits==32:return v&0xffffff
        return ((v>>8)&0xf800)|((v>>5)&0x7e0)|((v>>3)&31) if red==0xf800 else ((v>>9)&0x7c00)|((v>>6)&0x3e0)|((v>>3)&31)
    screens=[bytearray(),bytearray()]
    for i in range(5):
        p=f'p.s{i}.';ox,oy=(144,112) if i>=2 else (64,64);cover=i in (1,2)
        d[p+'origin.x']=ox;d[p+'origin.y']=oy
        for k in ('cover','cover.visible'):d[p+k]=int(cover)
        for k in ('cover.above','clip.exact','complete','before.capture','after.capture','post.valid'):d[p+k]=1
        for k in ('clip.size','clip.list','primary.blit','before.mismatches','after.mismatches','post.lock','post.unlock'):d[p+k]=0
        d[p+'post.pitch']=256;d[p+'post.caps']=0x2840
        for when in range(2):
            for k in ('lock','unlock','mismatches'):d[p+f'native{when}.'+k]=0
            d[p+f'native{when}.valid']=1;d[p+f'native{when}.pitch']=64*(bits//8);d[p+f'native{when}.caps']=0x840
        rects=[(8,8,56,24),(8,24,24,48),(48,24,56,48),(8,48,56,56)] if cover else [(8,8,56,56)]
        d[p+'clip.count']=len(rects);d[p+'clip.bytes']=32+len(rects)*16
        for j,r in enumerate(rects):
            for edge,v,offset in zip(('left','top','right','bottom'),r,(ox,oy,ox,oy)):d[p+f'clip.r{j}.'+edge]=v+offset
        for y in range(80):
            for x in range(80):
                target=8<=x<56 and 8<=y<56;occluded=cover and 24<=x<48 and 24<=y<48
                v=0xff00ff if occluded else 0 if target else 255
                screens[0]+=struct.pack('<I',packed(v))
                screens[1]+=struct.pack('<I',packed(pixels[i*4096+y*64+x] if target and not occluded else v))
    d.pop('end');d['end']='complete'
    native=b''.join(struct.pack('<I',packed(v)) for v in pixels)
    return d,data+[bytes(screens[0]),bytes(screens[1]),data[1],native,native]

class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.d,cls.data=fixture()
    def check(self,d=None,data=None):return g.validate(base.encode(self.d if d is None else d),*(self.data if data is None else data),'default',0)
    def test_valid(self):
        for bits,red in ((16,0xf800),(16,0x7c00),(32,0xff0000)):
            d,data=fixture(bits,red);self.assertTrue(self.check(d,data)['passed'])
    def test_metadata(self):
        for k in self.d:
            if not k.startswith('p.'):continue
            d=dict(self.d);d.pop(k)
            with self.assertRaises(ValueError,msg=k):self.check(d)
        for k,v in [('p.mode.bits',8),('p.mode.width',0),('p.s1.clip.r0.right',119),('p.s2.origin.x',64),
                    ('p.s0.post.caps',0x4200),('p.s0.post.pitch',255),('p.primary.detach',1),('p.extra',0)]:
            d=dict(self.d);d[k]=v
            with self.assertRaises(ValueError,msg=k):self.check(d)
    def test_pixels_and_lengths(self):
        for stream in range(9):
            for size in (-1,1):
                data=list(self.data);data[stream]=data[stream][:-1] if size<0 else data[stream]+b'\0'
                with self.assertRaises(ValueError):self.check(data=data)
        for stage in range(5):
            for stream,width in ((4,80),(5,80),(6,64),(7,64),(8,64)):
                for x,y in ((0,0),(12,12),(25,25),(50,50)):
                    data=list(self.data);b=bytearray(data[stream]);offset=(stage*width*width+y*width+x)*4;b[offset]^=1;data[stream]=b
                    with self.assertRaises(ValueError):self.check(data=data)
    def test_no_blank_or_stale_presentation(self):
        data=list(self.data);data[5]=data[4]
        with self.assertRaises(ValueError):self.check(data=data)
        data=list(self.data);b=bytearray(data[5]);b[4*25600:5*25600]=b[:25600];data[5]=b
        with self.assertRaises(ValueError):self.check(data=data)
if __name__=='__main__':unittest.main()
