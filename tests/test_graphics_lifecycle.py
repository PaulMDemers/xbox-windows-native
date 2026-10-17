#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Synthetic transport negatives and independently generated reference pixels."""
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_lifecycle as g


def fixture():
    d = dict(schema='xwn-lifecycle-1', backend='default', scope='system-memory-churn',
             warmup='8', cycles='64', completed_cycles='64', restore_exercised='0',
             exit='0', result='LIFECYCLE_OK', end='complete')
    d.update({'focus.scope': 'calling-thread-only', 'windows.created': '1',
              'os.major': '5', 'os.minor': '0', 'os.build': '2195',
              'mode.width': '640', 'mode.height': '480', 'mode.bpp': '16',
              'invalid.hr': '2147942487', 'invalid.null': '1',
              'memory.base': '2097152', 'memory.max_growth': '0',
              'memory.budget': '1048576', 'w8.memory.commit': '2097152',
              'w8.memory.working': '4194304'})
    for key in ('ddraw.load', 'ddraw.entry', 'psapi.load', 'psapi.entry',
                'focus.a', 'focus.b', 'focus.return', 'cleanup.modules'):
        d[key] = '1'
    for key in ('ddraw.create', 'ddraw.cooperative', 'ddraw.mode', 'release.ddraw'):
        d[key] = '0'
    for prefix, count in (('w', 8), ('c', 64)):
        for i in range(count):
            s = f'{prefix}{i}.'
            for key in ('src.create', 'dst.create', 'src.islost', 'dst.islost',
                        'blt', 'src.release', 'dst.release'):
                d[s+key] = '0'
            d[s+'complete'] = '1'
            for name in ('src.write', 'dst.write', 'src.read', 'dst.read'):
                for suffix, value in (('lock', '0'), ('unlock', '0'), ('layout', '1'), ('pitch', '512')):
                    d[s+name+'.'+suffix] = value
                if name.endswith('read'):
                    d[s+name+'.bad'] = '0'
            if prefix == 'c':
                d[s+'memory.commit'] = '2097152'
                d[s+'memory.working'] = '4194304'
    data = bytearray()
    for n in range(8, 72):
        source = [((5*x+13*n)&255)*65536+((11*y+7*n)&255)*256+(x^y^n) for y in range(96) for x in range(128)]
        dest = [0x19243b]*12288
        for y in range(72):
            dest[(y+11)*128+9:(y+11)*128+105] = source[(y+5)*128+3:(y+5)*128+99]
        data.extend(struct.pack('<12288I', *source))
        data.extend(struct.pack('<12288I', *dest))
    return d, bytes(data)


def encode(d):
    return ''.join(k+'='+v+'\r\n' for k, v in d.items()).encode()


class LifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fields, cls.pixels = fixture()

    def test_reference_and_backends(self):
        for backend in ('default', 'hel'):
            d = dict(self.fields, backend=backend)
            result = g.validate(encode(d), self.pixels, backend, 0)
            self.assertEqual(result['exact_bytes'], 6291456)
            self.assertFalse(result['actual_loss_restore_qualified'])

    def test_transport_and_lifetime_negatives(self):
        for key in self.fields:
            d = dict(self.fields); d[key] = '?'
            with self.assertRaises(ValueError, msg=key):
                g.validate(encode(d), self.pixels, 'default', 0)
        for key, value in [('invalid.hr', '0'), ('restore_exercised', '1'),
                           ('c63.src.release', '1'), ('c0.src.islost', '2147500037'),
                           ('c63.memory.commit', '3145729'), ('memory.max_growth', '1'),
                           ('memory.budget', '4294967295'), ('w8.memory.commit', '1'),
                           ('c0.src.read.pitch', '511'), ('focus.return', '0')]:
            d = dict(self.fields); d[key] = value
            with self.assertRaises(ValueError, msg=key):
                g.validate(encode(d), self.pixels, 'default', 0)
        raw = encode(self.fields)
        for changed in (raw+b'end=complete\r\n', raw.replace(b'c63.complete=1\r\n', b'')):
            with self.assertRaises(ValueError):g.validate(changed, self.pixels, 'default', 0)
        for code in (1, 2, 4, True, '0'):
            with self.assertRaises(ValueError):g.validate(raw, self.pixels, 'default', code)

    def test_every_cycle_source_copy_guard_and_length(self):
        raw = encode(self.fields)
        for i in range(64):
            for offset in (0, 49148, 49152, 49152+4*(11*128+9), 98300):
                data = bytearray(self.pixels);data[i*98304+offset] ^= 1
                with self.assertRaises(ValueError):g.validate(raw, bytes(data), 'default', 0)
        for data in (self.pixels[:-1], self.pixels+b'\0'):
            with self.assertRaises(ValueError):g.validate(raw, data, 'default', 0)


if __name__ == '__main__':
    unittest.main()
