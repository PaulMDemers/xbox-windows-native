#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate three complete scene captures and report whole-process telemetry."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import graphics_scenepresent as scene


def validate_report(raw, backend, exit_code):
    def need(value, message):
        if not value:
            raise ValueError(message)
    need(backend in ('default', 'hel') and exit_code == 0, 'Backend or wrapper exit')
    f = scene.scene.decode(raw)
    fixed = {'schema': 'xwn-scene-bench-1', 'backend': backend,
             'scope': 'three-child-processes-including-pauses-and-capture-io',
             'iterations': '3', 'poll_ms': '50', 'child_deadline_ms': '50000',
             'os.major': '5', 'os.minor': '0', 'os.build': '2195',
             'psapi.load': '1', 'psapi.entry': '1', 'psapi.unload': '1',
             'completed': '3', 'exit': '0', 'end': 'complete'}
    need(all(f.get(k) == v for k, v in fixed.items()), 'Fixed report fields')
    fields = ('available_before physical_total start_tick pid elapsed_ms wait exit '
              'samples min_ws max_ws peak_ws max_commit peak_commit first_faults '
              'last_faults handles_closed available_after complete').split()
    fields += [a + '.' + b for a in ('created', 'ended', 'kernel', 'user') for b in ('low', 'high')]
    wanted = set(fixed)
    rows = []
    for i in range(3):
        stem = f'c{i}.'
        keys = {stem + n for n in fields}
        if stem + 'exit_sample_race' in f:
            need(f[stem + 'exit_sample_race'] == '1', 'Exit race flag')
            keys.add(stem + 'exit_sample_race')
        wanted |= keys
        need(keys <= f.keys(), 'Missing child field')
        need(all(re.fullmatch(r'0|[1-9][0-9]*', f[k]) and int(f[k]) <= 0xffffffff for k in keys), 'Invalid DWORD')
        n = {k[len(stem):]: int(f[k]) for k in keys}
        need(n['pid'] > 0 and n['wait'] == n['exit'] == 0, 'Child did not exit successfully')
        need(n['handles_closed'] == n['complete'] == 1, 'Child cleanup/completion')
        need(0 < n['elapsed_ms'] < 50000 and 0 < n['samples'] <= 1000, 'Child deadline/samples')
        need(n['samples'] * 50 <= n['elapsed_ms'] + 50, 'Sample cadence inconsistent')
        need(0 < n['min_ws'] <= n['max_ws'] <= n['peak_ws'] <= n['physical_total'], 'Working-set bounds')
        need(0 < n['max_commit'] <= n['peak_commit'], 'Commit bounds')
        need(n['first_faults'] <= n['last_faults'], 'Page-fault counters reversed')
        need(n['available_before'] <= n['physical_total'] and n['available_after'] <= n['physical_total'], 'Global memory bounds')
        ticks = {k: (n[k + '.high'] << 32) | n[k + '.low'] for k in ('created', 'ended', 'kernel', 'user')}
        need(0 < ticks['created'] <= ticks['ended'], 'Process timestamps reversed')
        # Process time and GetTickCount are different clocks; allow coarse NT5 resolution.
        need(ticks['ended'] - ticks['created'] <= (n['elapsed_ms'] + 1000) * 10000, 'Lifetime inconsistent')
        need(ticks['kernel'] + ticks['user'] <= (n['elapsed_ms'] + 1000) * 10000, 'Single-thread CPU time inconsistent')
        rows.append(dict(iteration=i, elapsed_ms=n['elapsed_ms'],
                         kernel_ms=ticks['kernel'] / 10000, user_ms=ticks['user'] / 10000,
                         min_working_set=n['min_ws'], sampled_max_working_set=n['max_ws'],
                         reported_peak_working_set=n['peak_ws'], sampled_max_commit=n['max_commit'],
                         reported_peak_commit=n['peak_commit'], samples=n['samples'],
                         sampled_page_fault_delta=n['last_faults']-n['first_faults'],
                         available_before=n['available_before'], available_after=n['available_after']))
    need(set(f) == wanted, 'Unexpected report field')
    need(len({f[f'c{i}.physical_total'] for i in range(3)}) == 1, 'Physical memory changed')
    for i in (1, 2):
        delta = (int(f[f'c{i}.start_tick']) - int(f[f'c{i-1}.start_tick'])) & 0xffffffff
        need(int(f[f'c{i-1}.elapsed_ms']) <= delta < 60000, 'Child sequence inconsistent')
    return dict(passed=True, backend=backend, rows=rows,
                scope='Whole scene processes including startup, pauses, CPU conversion and capture I/O; no FPS, leak-free or GPU claim')


def validate_directory(prefix, backend):
    prefix = Path(prefix)
    if not re.fullmatch(r'[A-Za-z0-9-]{1,48}', prefix.name):
        raise ValueError('Invalid leaf prefix')
    raw = prefix.with_name(prefix.name + '-bench.txt').read_bytes()
    receipt = prefix.with_suffix('.exit').read_bytes()
    if receipt.strip() != b'0':
        raise ValueError('Wrapper exit receipt is not zero')
    result = validate_report(raw, backend, 0)
    results = []
    for i in range(3):
        p = prefix.with_name(prefix.name + f'-c{i}')
        data = p.with_suffix('.txt').read_bytes()
        if p.with_suffix('.exit').read_bytes().strip() != b'0':
            raise ValueError('Scene exit receipt is not zero')
        frames = [p.with_name(p.name + '-' + s + '.bin').read_bytes() for s in scene.SUFFIXES]
        results.append(scene.validate(data, *frames, backend, 0))
    result.update(scene_reviews=results, report_sha256=hashlib.sha256(raw).hexdigest())
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', required=True, choices=('default', 'hel'))
    a = p.parse_args()
    print(json.dumps(validate_directory(a.prefix, a.backend), indent=2))
