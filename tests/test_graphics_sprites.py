# SPDX-License-Identifier: MIT
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import graphics_sprites as g


def fixture(fmt, backend='default'):
    r = g.requirements(backend, fmt)
    del r['end']
    r.update({'mode.width':640, 'mode.height':480, 'mode.bpp':16})
    for s in range(4):
        for label in ('source.read', 'dest.read') + (('source.write', 'dest.write') if s == 0 else ()):
            r[f's{s}.{label}.pitch'] = (16 if label.startswith('source') else 32)*g.FORMATS[fmt]//8
    r['end'] = 'complete'
    return r, g.oracle(fmt)


def encode(r):
    return ''.join(f'{k}={v}\r\n' for k,v in r.items()).encode('ascii')


class Sprites(unittest.TestCase):
    def test_desktop_depth_is_independent_of_surface_format(self):
        for fmt in g.FORMATS:
            r, captures = fixture(fmt)
            for depth in (16, 24, 32):
                r['mode.bpp'] = depth
                self.assertTrue(g.validate(encode(r), captures, 'default', fmt, 0)['passed'])
            for depth in (0, 1, 4, 8, 15, 23, 25, 48, '024', '-24'):
                r['mode.bpp'] = depth
                with self.subTest(fmt=fmt, depth=depth), self.assertRaises(ValueError):
                    g.validate(encode(r), captures, 'default', fmt, 0)
            r['mode.bpp'] = 24
            changed = dict(captures)
            changed['dest'] = bytes([captures['dest'][0] ^ 1]) + captures['dest'][1:]
            with self.assertRaises(ValueError):
                g.validate(encode(r), changed, 'default', fmt, 0)

    def test_oracle_semantics(self):
        o = g.oracle('index8')
        frames = [struct.unpack('<768I', o['dest'][s*3072:(s+1)*3072]) for s in range(4)]
        # Keyed zero at source(2,3) keeps background; clip gap remains untouched.
        self.assertEqual(frames[0][7*32+6], 200)
        self.assertEqual(frames[0][6*32+13], 200)
        self.assertEqual(frames[0][5*32+6], 14)
        self.assertEqual(frames[0], frames[1])
        self.assertNotEqual(o['rgb'][:3072], o['rgb'][3072:6144])
        for y in range(12):
            self.assertEqual(frames[2][(6+y)*32+7:(6+y)*32+23], frames[1][(4+y)*32+4:(4+y)*32+20])
            self.assertEqual(frames[3][(3+y)*32+3:(3+y)*32+19], frames[2][(6+y)*32+7:(6+y)*32+23])

    def test_valid_and_refusals(self):
        for fmt in g.FORMATS:
            r,c = fixture(fmt)
            self.assertEqual(g.validate(encode(r),c,'default',fmt,0)['exact_bytes'],31744 if fmt=='index8' else 27648)
            for k,v in list(r.items()):
                if k == 'end': continue
                bad = dict(r); bad[k] = 'invalid'
                with self.subTest(fmt=fmt,key=k), self.assertRaises(ValueError):
                    g.validate(encode(bad),c,'default',fmt,0)
            for k in c:
                bad = dict(c); bad[k] += b'\0'
                with self.assertRaises(ValueError): g.validate(encode(r),bad,'default',fmt,0)
                for off in range(0,len(c[k]),257):
                    bad = dict(c); changed = bytearray(c[k]); changed[off] ^= 1; bad[k] = bytes(changed)
                    with self.assertRaises(ValueError): g.validate(encode(r),bad,'default',fmt,0)
            for raw in (encode(r)[:-2],b'exit=0\r\n'+encode(r)):
                with self.assertRaises(ValueError): g.validate(raw,c,'default',fmt,0)
            with self.assertRaises(ValueError): g.validate(encode(r),c,'default',fmt,1)
            with self.assertRaises(ValueError): g.validate(encode(r),c,'hel',fmt,0)


if __name__ == '__main__': unittest.main()
