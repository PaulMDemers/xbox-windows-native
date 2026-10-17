#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent bounded lifecycle receipt and raw-pixel checker."""
import argparse
from pathlib import Path
import struct
from functools import lru_cache

WIDTH, HEIGHT, WARMUP, CYCLES, BUDGET = 128, 96, 8, 64, 1048576


def decode(raw):
    if not 0 < len(raw) <= 262144:
        raise ValueError('Missing or oversized report')
    result = {}
    for line in raw.decode('ascii').splitlines():
        key, sep, value = line.partition('=')
        if not sep or not key or not value or key in result:
            raise ValueError('Malformed/duplicate field')
        result[key] = value
    return result


@lru_cache(maxsize=CYCLES*2)
def frame(cycle, source):
    """Generate packed independent reference pixels; never consume guest hashes."""
    result = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if not source and not (9 <= x < 105 and 11 <= y < 83):
                value = 0x19243b
            else:
                sx, sy = (x, y) if source else (x-6, y-6)
                red = (cycle*13 + sx*5) % 256
                green = (cycle*7 + sy*11) % 256
                blue = (sx ^ sy ^ cycle) % 256
                value = red*65536 + green*256 + blue
            result += struct.pack('<I', value)
    return bytes(result)


def validate(raw, pixels, backend, process_exit):
    if backend not in ('default', 'hel') or type(process_exit) is not int or process_exit != 0:
        raise ValueError('Backend or external exit failure')
    fields = decode(raw)
    expected = dict(schema='xwn-lifecycle-1', backend=backend,
                    scope='system-memory-churn', **{'focus.scope': 'calling-thread-only'},
                    warmup='8', cycles='64', **{'windows.created': '1',
                    'ddraw.load': '1', 'ddraw.entry': '1', 'psapi.load': '1',
                    'psapi.entry': '1', 'ddraw.create': '0', 'ddraw.cooperative': '0',
                    'ddraw.mode': '0', 'invalid.null': '1', 'focus.a': '1',
                    'focus.b': '1', 'focus.return': '1', 'release.ddraw': '0',
                    'cleanup.modules': '1'},
                    completed_cycles='64', restore_exercised='0', exit='0',
                    result='LIFECYCLE_OK', end='complete')
    numeric = {'os.major', 'os.minor', 'os.build', 'mode.width', 'mode.height',
               'mode.bpp', 'invalid.hr', 'memory.base', 'memory.max_growth', 'memory.budget',
               'w8.memory.commit', 'w8.memory.working'}
    pitches = set()
    for prefix, count in (('w', WARMUP), ('c', CYCLES)):
        for cycle in range(count):
            stem = f'{prefix}{cycle}.'
            for key in ('src.create', 'dst.create', 'src.islost', 'dst.islost',
                        'blt', 'src.release', 'dst.release'):
                expected[stem+key] = '0'
            expected[stem+'complete'] = '1'
            for operation in ('src.write', 'dst.write', 'src.read', 'dst.read'):
                for key, value in (('lock', '0'), ('layout', '1'), ('unlock', '0')):
                    expected[stem+operation+'.'+key] = value
                pitches.add(stem+operation+'.pitch')
                if operation.endswith('read'):
                    expected[stem+operation+'.bad'] = '0'
            if prefix == 'c':
                numeric.update((stem+'memory.commit', stem+'memory.working'))
    if set(fields) != set(expected) | numeric | pitches:
        raise ValueError('Incomplete or unknown fields')
    for key, value in expected.items():
        if fields[key] != value:
            raise ValueError('Unexpected '+key)
    values = {}
    for key in numeric | pitches:
        v = fields[key]
        if not v.isascii() or not v.isdecimal() or str(int(v)) != v or not 0 <= int(v) <= 0xffffffff:
            raise ValueError('Invalid scalar '+key)
        values[key] = int(v)
    if any(not WIDTH*4 <= values[p] <= 65536 or values[p] % 4 for p in pitches):
        raise ValueError('Invalid pitch')
    if not values['invalid.hr'] & 0x80000000:
        raise ValueError('Malformed descriptor unexpectedly accepted')
    if not (0 < values['mode.width'] <= 8192 and 0 < values['mode.height'] <= 8192
            and values['mode.bpp'] in (16, 24, 32)):
        raise ValueError('Invalid desktop mode')
    base = values['memory.base']
    growth = max(0, *(values[f'c{i}.memory.commit']-base for i in range(CYCLES)))
    if base == 0 or values['w8.memory.commit'] != base or values['memory.budget'] != BUDGET or values['memory.max_growth'] != growth or growth > BUDGET:
        raise ValueError('Memory bound or receipt mismatch')
    size = WIDTH*HEIGHT*4
    if len(pixels) != CYCLES*2*size:
        raise ValueError('Truncated/extra capture bytes')
    for i in range(CYCLES):
        for j, source in enumerate((True, False)):
            if pixels[(i*2+j)*size:(i*2+j+1)*size] != frame(i+WARMUP, source):
                raise ValueError(f'Pixel mismatch cycle{i} source={source}')
    return dict(passed=True, exact_bytes=len(pixels), measured_cycles=CYCLES,
                warmup_cycles=WARMUP, max_commit_growth=growth, budget=BUDGET,
                focus_scope='calling thread only', actual_loss_restore_qualified=False,
                gpu_qualified=False, leak_freedom_proved=False)


def main():
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', choices=('default', 'hel'), required=True)
    a = p.parse_args()
    root = str(a.prefix)
    code = Path(root+'.exit').read_text().strip()
    if code != '0':
        raise ValueError('External exit must be0')
    print(json.dumps(validate(Path(root+'.txt').read_bytes(), Path(root+'-pixels.bin').read_bytes(), a.backend, 0), indent=2))


if __name__ == '__main__':
    main()
