#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate and summarize XWN inventory JSON; no network or console access."""
import argparse
import json
from pathlib import Path

KEYS = {'schema', 'tool', 'kernel', 'hardware_flags', 'gpu_revision', 'mcp_revision',
        'memory_status', 'kernel_total_pages', 'page_bytes', 'video_settings', 'av_pack',
        'video_standard', 'encoder_probe', 'e_space', 'available_32bit_modes', 'pci', 'complete'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def integer(x, high=0xffffffff):
    require(type(x) is int and 0 <= x <= high, 'Invalid unsigned integer')


def keys(obj, names):
    require(isinstance(obj, dict) and set(obj) == set(names), 'Unexpected/missing fields; do not submit private data')


def validate(r):
    require(isinstance(r, dict), 'Report must be an object')
    version = r.get('schema')
    require(type(version) is int and version in (1, 2), 'Unknown tool/schema')
    keys(r, KEYS | ({'pci_scan_policy'} if version == 2 else set()))
    require(r['tool'] == f'xwn-hardware-report-{version}', 'Unknown tool/schema')
    if version == 2:
        require(r['pci_scan_policy'] == 'xbox-safe-v1', 'Unknown PCI scan policy')
    require(r['complete'] is True, 'Incomplete report')
    require(isinstance(r['kernel'], list) and len(r['kernel']) == 4, 'Kernel version shape')
    for v in r['kernel']: integer(v, 65535)
    for n in ('hardware_flags', 'memory_status', 'kernel_total_pages', 'video_settings', 'av_pack', 'video_standard'):
        integer(r[n])
    for n in ('gpu_revision', 'mcp_revision'): integer(r[n], 255)
    require(r['page_bytes'] == 4096 and type(r['page_bytes']) is int, 'Unexpected page size')
    require(r['av_pack'] == r['video_settings'] & 255 and r['video_standard'] == r['video_settings'] & 0xff00, 'Video mask mismatch')
    e = r['encoder_probe']
    keys(e, ('label', 'conexant_status', 'conexant_value', 'focus_status', 'focus_value'))
    for n in ('conexant_status', 'conexant_value', 'focus_status', 'focus_value'): integer(e[n])
    expected = 'conexant-response' if e['conexant_status'] == 0 and e['focus_status'] != 0 else (
        'focus-response' if e['focus_status'] == 0 and e['conexant_status'] != 0 else 'unidentified')
    require(e['label'] == expected, 'Unsupported encoder inference')
    s = r['e_space']; keys(s, ('ok', 'free_bytes', 'total_bytes'))
    require(type(s['ok']) is bool, 'Invalid space status')
    for n in ('free_bytes', 'total_bytes'): integer(s[n], 2**64-1)
    require(s['free_bytes'] <= s['total_bytes'], 'Invalid space totals')
    modes = r['available_32bit_modes']
    require(isinstance(modes, list) and len(modes) < 128, 'Mode capacity exceeded')
    for mode in modes:
        require(isinstance(mode, list) and len(mode) == 4, 'Invalid mode')
        for v in mode: integer(v, 8192)
        require(mode[0] > 0 and mode[1] > 0 and mode[2] == 32 and 0 < mode[3] <= 240, 'Invalid mode values')
    require(len({tuple(m) for m in modes}) == len(modes), 'Duplicate mode')
    pci = r['pci']; require(isinstance(pci, list) and len(pci) <= 512, 'PCI capacity exceeded')
    slots = set()
    for d in pci:
        keys(d, ('bus', 'device', 'function', 'id', 'class_revision'))
        for n, high in [('bus', 1), ('device', 31), ('function', 7), ('id', 0xffffffff), ('class_revision', 0xffffffff)]: integer(d[n], high)
        slot = (d['bus'], d['device'], d['function'])
        if version == 2:
            require(slot not in ((0, 0, 1), (0, 0, 2)) and not (slot[0] == 1 and slot[1] != 0),
                    'Report includes a location excluded by its PCI policy')
        require(slot not in slots and d['id'] & 0xffff not in (0, 65535), 'Duplicate/absent PCI device')
        slots.add(slot)
    return r


def unique(pairs):
    out = {}
    for k, v in pairs:
        require(k not in out, 'Duplicate JSON key'); out[k] = v
    return out


def load(path):
    require(path.stat().st_size < 32768, 'Report size bound')
    return validate(json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique))


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('report', type=Path); a = p.parse_args()
    r = load(a.report)
    memory = r['kernel_total_pages'] / 256 if r['memory_status'] == 0 else None
    print(json.dumps(dict(kernel=r['kernel'], encoder_observation=r['encoder_probe']['label'],
        kernel_reported_ram_mib=memory, pci_response_records=len(r['pci']), e_space=r['e_space'],
        available_modes=r['available_32bit_modes'], compatibility='Not established by this inventory'), indent=2))


if __name__ == '__main__':
    main()
