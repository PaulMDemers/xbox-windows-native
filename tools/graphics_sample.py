#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Read graphics ladder evidence with an independent RGB oracle. Does not launch."""
import argparse
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def decode(raw):
    require(0 < len(raw) <= 32768, 'Missing/oversized report')
    lines = raw.decode('ascii').splitlines()
    fields = {}
    for line in lines:
        key, sep, value = line.partition('=')
        require(sep and key and value and key not in fields, 'Malformed/duplicate report field')
        fields[key] = value
    require(lines[-1] == 'end=complete', 'Terminal completion missing or not last')
    require(fields.get('schema') == 'xwn-graphics-ladder-1', 'Unknown schema')
    require(fields.get('scope') == 'user-mode-sample', 'Unknown scope')
    require(fields.get('rung') in ('00', '01', '02'), 'Unknown rung')
    require(fields.get('backend') in ('default', 'hel', 'hal'), 'Unknown backend')
    require(not (fields['rung']=='02' and fields['backend']=='hal'), 'Hardware-only system-memory path not qualified for this rung')
    require(fields.get('display') in ('quiet', 'view'), 'Unknown display request')
    require(fields.get('visual') == 'UNVERIFIED', 'Automated report cannot qualify visual output')
    require(fields.get('exit') == '0', 'Sample recorded failure')
    return fields


def expected():
    # Independent implementation: build planar channels, then pack B,G,R,zero.
    # The 48x32 copy has source origin (3,4), destination origin (8,10).
    source = bytearray()
    for row in range(48):
        for col in range(64):
            source.extend(((7*col+19*row) % 256, (5*col+11*row) % 256,
                           (17*col+3*row) % 256, 0))
    dest = bytearray(bytes((0x47, 0x29, 0x13, 0))*96*80)
    for row in range(32):
        src = ((row+4)*64+3)*4
        dst = ((row+10)*96+8)*4
        dest[dst:dst+48*4] = source[src:src+48*4]
    return bytes(source), bytes(dest)


def validate(fields, source=None, dest=None, process_exit=0):
    require(process_exit == 0, 'Actual process exit was not successful')
    rung = fields['rung']
    require(fields.get('window.create') == '1', 'Window creation not acknowledged')
    for key in ('os.api.major','os.api.minor','os.api.build','os.api.platform'):
        require(fields.get(key, '').isdigit(), 'Missing OS API identity')
    if rung == '00':
        require(fields['backend'] == 'default', 'GDI backend must be default')
        for key in ('dc','dib','select','blit','flush','cleanup'):
            require(fields.get('gdi.'+key) == '1', 'GDI operation failed/missing: '+key)
    else:
        for key in ('ddraw.load','ddraw.entry','ddraw.unload'):
            require(fields.get(key) == '1', 'DirectDraw module step failed/missing')
        for key in ('ddraw.create','ddraw.cooperative','ddraw.caps','ddraw.mode'):
            require(fields.get(key) == '00000000', 'API step failed/missing: '+key)
        for owner in ('hardware','hel'):
            for name in ('dwCaps','dwCaps2','dwCKeyCaps','dwFXCaps','dwPalCaps','dwVidMemTotal','dwVidMemFree'):
                value = fields.get('caps.'+owner+'.'+name, '')
                require(value.isdigit() and 0 <= int(value) <= 0xffffffff, 'Missing/invalid caps')
        for name in ('width','height','bpp'):
            value=fields.get('mode.'+name, '')
            require(value.isdigit() and 0 < int(value) <= 65536, 'Missing/invalid mode')
        require(fields.get('release.ddraw', '').isdigit(), 'Missing object release call')
    if rung == '02':
        for key in ('surface.source.create','surface.dest.create','surface.blit'):
            require(fields.get(key) == '00000000', 'Surface operation failed/missing: '+key)
        for owner,w in (('source',64),('dest',96)):
            require(fields.get('release.'+owner, '').isdigit(), 'Missing surface release call')
            for phase in ('write','read'):
                prefix=owner+'.'+phase
                require(fields.get(prefix+'.lock') == '00000000', 'Missing successful lock')
                require(fields.get(prefix+'.unlock') == '00000000', 'Missing successful unlock')
                require(fields.get(prefix+'.layout') == '1', 'Surface layout refused')
                pitch=fields.get(prefix+'.pitch', '')
                require(pitch.isdigit() and w*4 <= int(pitch) <= 65536 and int(pitch)%4 == 0,
                        'Invalid surface pitch')
    if rung == '01':
        require(fields.get('result') == 'INVENTORY_OK', 'Wrong inventory result')
        require(source is None and dest is None, 'Inventory has unexpected pixel evidence')
    else:
        require(fields.get('result') == 'PIXELS_OK' and fields.get('pixels.mismatches') == '0',
                'Pixel result did not pass')
        es, ed = expected()
        require(source == es, 'Source capture differs from independent oracle')
        require(dest == ed, 'Destination capture differs from independent copy/guard oracle')
    return dict(rung=rung, backend_requested=fields['backend'],
                result='inventory-complete' if rung=='01' else 'pixel-data-verified',
                checked_rgb_pixels=0 if rung=='01' else 64*48+96*80,
                visual_qualified=False, hardware_acceleration_proved=False,
                nt5_or_xbox_qualified=False)


def review(prefix, exit_file):
    path=Path(str(prefix)+'.txt')
    raw=path.read_bytes()
    fields=decode(raw)
    exit_text=Path(exit_file).read_text(encoding='ascii').strip()
    require(exit_text == '0', 'External exit record is not zero')
    sp,dp=Path(str(prefix)+'-source.bin'),Path(str(prefix)+'-dest.bin')
    if fields['rung']=='01':
        require(not sp.exists() and not dp.exists(), 'Unexpected inventory capture files')
        source=dest=None
    else:
        require(sp.stat().st_size == 12288 and dp.stat().st_size == 30720, 'Capture length mismatch')
        source,dest=sp.read_bytes(),dp.read_bytes()
    result=validate(fields,source,dest,int(exit_text))
    result['sha256']={'report':hashlib.sha256(raw).hexdigest()}
    if source is not None:
        result['sha256'].update(source=hashlib.sha256(source).hexdigest(),dest=hashlib.sha256(dest).hexdigest())
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prefix', required=True, type=Path)
    p.add_argument('--exit-file', required=True, type=Path)
    a=p.parse_args()
    print(json.dumps(review(a.prefix,a.exit_file),indent=2))


if __name__=='__main__':
    main()
