#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decode bounded D3D7 inventory; declared caps never qualify a real draw."""
import argparse
import json
from pathlib import Path
import struct
import uuid

CAP_BYTES, CAPACITY = 236, 16
SCALARS = {'caps': (0, 'I'), 'render_depths': (116, 'I'), 'z_depths': (120, 'I'),
           'max_texture_width': (132, 'I'), 'max_texture_height': (136, 'I'),
           'texture_ops': (180, 'I'), 'blend_stages': (184, 'H'), 'textures': (186, 'H')}


def decode(raw):
    if not 0 < len(raw) <= 65536:
        raise ValueError('Report size invalid')
    result = {}
    for line in raw.decode('ascii').splitlines():
        key, sep, value = line.partition('=')
        if not sep or not key or not value or key in result:
            raise ValueError('Malformed or duplicate field')
        result[key] = value
    return result


def integer(value):
    if not value.isascii() or not value.isdecimal() or str(int(value)) != value or not 0 <= int(value) <= 0xffffffff:
        raise ValueError('Invalid unsigned scalar')
    return int(value)


def unhex(value, low, high):
    raw = bytes.fromhex(value)
    if raw.hex() != value or not low <= len(raw) <= high:
        raise ValueError('Invalid hex field')
    return raw


def validate(raw, caps, backend, process_exit):
    if backend not in ('default', 'hel') or type(process_exit) is not int or process_exit != 0:
        raise ValueError('Invalid backend/exit')
    f = decode(raw)
    expected = dict(schema='xwn-d3d-discovery-1', backend=backend,
                    scope='capability-inventory-only', capacity='16', rendering_tested='0',
                    exit='0', result='INVENTORY_OK', end='complete',
                    **{'caps.bytes': '236', 'window.created': '1', 'ddraw.load': '1',
                       'ddraw.entry': '1', 'ddraw.create': '0', 'ddraw.cooperative': '0',
                       'ddraw.mode': '0', 'callback.error': '0', 'release.ddraw': '0', 'ddraw.unload': '1'})
    numeric = {'os.major', 'os.minor', 'os.build', 'mode.width', 'mode.height', 'mode.bpp', 'devices'}
    available = f.get('interface.status') == 'available'
    if available:
        expected.update({'interface.status': 'available', 'd3d.query': '0',
                         'd3d.pointer': '1', 'enum.called': '1', 'enum.hr': '0'})
        numeric.add('release.d3d')
    else:
        expected.update({'interface.status': 'unavailable', 'd3d.query': str(0x80004002),
                         'd3d.pointer': '0', 'enum.called': '0', 'devices': '0'})
    count = integer(f.get('devices', '?'))
    if count > CAPACITY or len(caps) != CAP_BYTES*count:
        raise ValueError('Count/capture mismatch or overflow')
    extra = set()
    rows, guids = [], set()
    for i in range(count):
        stem = f'd{i}.'
        names = set(SCALARS) | {'name', 'description', 'guid', 'raw',
                                'hardware_rasterization_reported', 'hardware_tnl_reported'}
        extra.update(stem+n for n in names)
        block = caps[i*CAP_BYTES:(i+1)*CAP_BYTES]
        if unhex(f.get(stem+'raw', ''), CAP_BYTES, CAP_BYTES) != block:
            raise ValueError('Raw capability transport mismatch')
        guid = unhex(f.get(stem+'guid', ''), 16, 16)
        if guid != block[196:212] or guid in guids:
            raise ValueError('Duplicate or mismatched GUID')
        guids.add(guid)
        values = {name: struct.unpack_from('<'+fmt, block, offset)[0] for name, (offset, fmt) in SCALARS.items()}
        for name, value in values.items():
            if integer(f.get(stem+name, '?')) != value:
                raise ValueError('Capability scalar mismatch: '+name)
        hardware = bool(values['caps'] & 0x80000)
        tnl = bool(values['caps'] & 0x10000)
        if f.get(stem+'hardware_rasterization_reported') != str(int(hardware)) or f.get(stem+'hardware_tnl_reported') != str(int(tnl)):
            raise ValueError('Capability classification mismatch')
        strings = {}
        for key in ('name', 'description'):
            value = unhex(f.get(stem+key, ''), 1, 255)
            if b'\0' in value:
                raise ValueError('Embedded terminator')
            strings[key] = value.decode('cp1252', errors='replace')
        rows.append(dict(guid=str(uuid.UUID(bytes_le=guid)), **strings, **values,
                         hardware_rasterization_reported=hardware, hardware_tnl_reported=tnl))
    if set(f) != set(expected) | numeric | extra:
        raise ValueError('Missing/unknown report fields')
    if any(f.get(key) != value for key, value in expected.items()):
        raise ValueError('Incomplete or failed inventory')
    n = {key: integer(f[key]) for key in numeric}
    if not 0 < n['mode.width'] <= 8192 or not 0 < n['mode.height'] <= 8192 or n['mode.bpp'] not in (16, 24, 32):
        raise ValueError('Invalid desktop mode')
    return dict(passed=True, interface_available=available, device_count=count,
                devices=rows, rendering_qualified=False, gpu_qualified=False,
                scope='Complete runtime capability declarations, no CreateDevice or draw')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', choices=('default', 'hel'), required=True)
    a = p.parse_args();root = str(a.prefix)
    if Path(root+'.exit').read_text().strip() != '0':
        raise ValueError('External process failed')
    print(json.dumps(validate(Path(root+'.txt').read_bytes(), Path(root+'-caps.bin').read_bytes(), a.backend, 0), indent=2))


if __name__ == '__main__':
    main()
