#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import struct
import sys
import unittest
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import graphics_discovery as g


def fixture(available=True, count=2):
    f = dict(schema='xwn-d3d-discovery-1', backend='default', scope='capability-inventory-only',
             capacity='16', rendering_tested='0', exit='0', result='INVENTORY_OK', end='complete', devices=str(count))
    f.update({'caps.bytes': '236', 'window.created': '1', 'ddraw.load': '1', 'ddraw.entry': '1',
              'ddraw.create': '0', 'ddraw.cooperative': '0', 'ddraw.mode': '0', 'callback.error': '0',
              'release.ddraw': '0', 'ddraw.unload': '1', 'os.major': '5', 'os.minor': '0',
              'os.build': '2195', 'mode.width': '640', 'mode.height': '480', 'mode.bpp': '16',
              'interface.status': 'available' if available else 'unavailable',
              'd3d.query': '0' if available else '2147500034', 'd3d.pointer': str(int(available)),
              'enum.called': str(int(available))})
    if available:f.update({'enum.hr': '0', 'release.d3d': '1'})
    data = bytearray()
    for i in range(count):
        b = bytearray(236)
        struct.pack_into('<I', b, 0, 0 if i == 0 else 0x90000)
        struct.pack_into('<II', b, 116, 1280, 1024)
        struct.pack_into('<II', b, 132, 2048, 2048)
        struct.pack_into('<IHH', b, 180, 0x600, 2, 2)
        b[196:212] = uuid.UUID(int=i+1).bytes_le
        data.extend(b);s = f'd{i}.'
        f.update({s+'raw': b.hex(), s+'guid': b[196:212].hex(), s+'name': b'model'.hex(),
                  s+'description': b'synthetic device'.hex(), s+'caps': str(0 if i == 0 else 0x90000),
                  s+'render_depths': '1280', s+'z_depths': '1024', s+'max_texture_width': '2048',
                  s+'max_texture_height': '2048', s+'texture_ops': '1536', s+'blend_stages': '2',
                  s+'textures': '2', s+'hardware_rasterization_reported': str(int(i != 0)),
                  s+'hardware_tnl_reported': str(int(i != 0))})
    return f, bytes(data)


def encode(f):return ''.join(k+'='+v+'\r\n' for k, v in f.items()).encode()


class DiscoveryTests(unittest.TestCase):
    def test_available_empty_unavailable(self):
        for available, count in [(True, 2), (True, 0), (False, 0), (True, 16)]:
            f, caps = fixture(available, count)
            for backend in ('default', 'hel'):
                f['backend'] = backend;r = g.validate(encode(f), caps, backend, 0)
                self.assertEqual(r['interface_available'], available)
                self.assertEqual(r['device_count'], count)
                self.assertFalse(r['rendering_qualified'])

    def test_every_scalar_and_raw_byte(self):
        f, caps = fixture();raw = encode(f)
        for key in f:
            altered = dict(f);altered[key] = '?'
            with self.assertRaises(ValueError, msg=key):g.validate(encode(altered), caps, 'default', 0)
        for offset in range(len(caps)):
            altered = bytearray(caps);altered[offset] ^= 1
            with self.assertRaises(ValueError):g.validate(raw, bytes(altered), 'default', 0)

    def test_identity_capacity_completion(self):
        f, caps = fixture();raw = encode(f)
        for key, value in [('devices', '17'), ('callback.error', '2'), ('enum.hr', '2147500037'),
                           ('d3d.pointer', '0'), ('d3d.query', '2147500034'), ('rendering_tested', '1'),
                           ('d0.hardware_rasterization_reported', '1'), ('d0.max_texture_width', '4096'),
                           ('d0.name', '00'), ('d0.description', 'ff'*256), ('release.ddraw', '1')]:
            changed = dict(f);changed[key] = value
            with self.assertRaises(ValueError, msg=key):g.validate(encode(changed), caps, 'default', 0)
        duplicate = bytearray(caps);duplicate[236+196:236+212] = caps[196:212]
        d = dict(f);d['d1.guid'] = f['d0.guid'];d['d1.raw'] = duplicate[236:].hex()
        with self.assertRaises(ValueError):g.validate(encode(d), bytes(duplicate), 'default', 0)
        for data in (caps[:-1], caps+b'\0'):
            with self.assertRaises(ValueError):g.validate(raw, data, 'default', 0)
        for data in (raw+b'end=complete\r\n', raw.replace(b'enum.hr=0\r\n', b''), raw+b'extra=1\r\n'):
            with self.assertRaises(ValueError):g.validate(data, caps, 'default', 0)
        for code in (1, True, '0'):
            with self.assertRaises(ValueError):g.validate(raw, caps, 'default', code)


if __name__ == '__main__':unittest.main()
