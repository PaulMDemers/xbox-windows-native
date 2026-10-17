# SPDX-License-Identifier: MIT
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import graphics_present as g


def fixture():
    r = dict(schema='xwn-present-2', rung='03', backend='default', visual='UNVERIFIED',
             scope='owned-window-gdi-readback', result='PRESENTATION_OK', exit=0)
    for k in ('ddraw.load', 'ddraw.entry', 'window.create', 'clipper.owner', 'ddraw.unload'):
        r[k] = 1
    for k in ('ddraw.create', 'ddraw.cooperative', 'ddraw.mode', 'primary.create', 'primary.format',
              'source.create', 'clipper.create', 'clipper.hwnd', 'clipper.gethwnd', 'primary.clipper', 'primary.detach'):
        r[k] = '00000000'
    for k in ('source', 'primary', 'clipper', 'ddraw'): r['release.'+k] = 0
    for k, v in zip(('flags','bits','red','green','blue'), (64,32,0xff0000,0xff00,255)): r['format.'+k] = v
    for k, v in {'mode.width':640,'mode.height':480,'mode.bpp':32,'os.major':5,'os.minor':0,'os.build':2195}.items(): r[k] = v
    for s in range(4):
        p = f's{s}.'; ox, oy = (64,64) if s < 2 else (144,112)
        r.update({p+'origin.x':ox,p+'origin.y':oy,p+'cover':int(s in (1,2))})
        r.update({p+'cover.visible':int(s in (1,2)),p+'cover.above':1,p+'cover.preabove':int(s>0)})
        for k in ('clip.size','clip.list','source.write.lock','source.read.lock','source.write.unlock','source.read.unlock','primary.blit'): r[p+k] = '00000000'
        for k in ('clip.exact','before.capture','after.capture','source.write.layout','source.read.layout','source.exact','complete'): r[p+k] = 1
        for k in ('before.mismatches','after.mismatches'): r[p+k] = 0
        for k in ('source.write.pitch','source.read.pitch'): r[p+k] = 512
        rects = [(16,16,112,96)] if s in (0,3) else [(16,16,112,40),(16,40,48,72),(88,40,112,72),(16,72,112,96)]
        r[p+'clip.count'] = len(rects); r[p+'clip.bytes'] = 32+16*len(rects)
        for i, rect in enumerate(rects):
            for k, v, offset in zip(('left','top','right','bottom'),rect,(ox,oy,ox,oy)): r[p+f'clip.r{i}.'+k] = v+offset
    r['end'] = 'complete'
    captures = {kind:b''.join(g.expected(s,kind) for s in range(4)) for kind in ('source','before','after')}
    return r, captures


def encode(r): return ''.join(f'{k}={v}\r\n' for k,v in r.items()).encode('ascii')


class Presentation(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report, cls.captures = fixture()
    def test_valid(self):
        self.assertEqual(g.validate(encode(self.report),self.captures,'default',0)['exact_bytes'],1802240)
    def test_clipping_movement_completion(self):
        for key,value in [('s1.clip.r0.bottom',160),('s2.origin.x',64),('s2.cover',0),
                          ('s3.complete',0),('s0.primary.blit','8876021C'),('s0.source.read.pitch',1),
                          ('release.primary',1),('s0.clip.count',65),('s0.clip.r0.left',79),
                          ('s1.clip.r1.left',111),('s0.before.mismatches',1),
                          ('s1.cover.visible',0),('s1.cover.above',0),('s0.cover.preabove',2)]:
            r = dict(self.report); r[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): g.validate(encode(r),self.captures,'default',0)
    def test_pixels_and_transport(self):
        for kind in self.captures:
            for offset in (0,4*(16*256+16),len(self.captures[kind])-1):
                c = dict(self.captures); changed = bytearray(c[kind]); changed[offset] ^= 1; c[kind] = bytes(changed)
                with self.assertRaises(ValueError): g.validate(encode(self.report),c,'default',0)
            c = dict(self.captures); c[kind] = c[kind][:-1]
            with self.assertRaises(ValueError): g.validate(encode(self.report),c,'default',0)
        with self.assertRaises(ValueError): g.validate(encode(self.report)[:-2],self.captures,'default',0)
        with self.assertRaises(ValueError): g.validate(b'exit=0\r\n'+encode(self.report),self.captures,'default',0)
        with self.assertRaises(ValueError): g.validate(encode(self.report),self.captures,'default',1)
        with self.assertRaises(ValueError): g.validate(encode(self.report),self.captures,'hel',0)


if __name__ == '__main__': unittest.main()
