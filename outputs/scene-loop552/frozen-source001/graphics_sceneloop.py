#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate sustained software scene endpoints and bounded phase telemetry."""
import argparse
import json
from pathlib import Path
import graphics_scenepresent as scene


def telemetry(f):
    seen = set()
    def num(key):
        key = 'loop.' + key
        seen.add(key)
        value = scene.scene.integer(f.get(key, '?'))
        if not 0 <= value < 2**32:
            raise ValueError('DWORD: ' + key)
        return value
    def need(key, expected):
        if num(key) != expected:
            raise ValueError('Loop field: ' + key)
    def wide(key):
        value = num(key + '.low') + (num(key + '.high') << 32)
        if value >= 2**63:
            raise ValueError('Signed counter overflow')
        return value
    for key in ('psapi.load', 'psapi.entry', 'psapi.unload'):
        need(key, 1)
    need('frames_per_stage', 32)
    need('batch_deadline_ms', 30000)
    frequency = wide('frequency')
    if not 1 <= frequency <= 10**10:
        raise ValueError('Counter frequency')
    memory = {}
    for stem in ['before'] + [f's{i}.{when}' for i in range(5) for when in ('before', 'after')] + ['released']:
        row = {n: num(f'mem.{stem}.{n}') for n in ('ws', 'peak_ws', 'commit', 'peak_commit', 'faults')}
        if not 0 < row['ws'] <= row['peak_ws'] <= 8*1024**2 or not 0 <= row['commit'] <= row['peak_commit'] <= 8*1024**2:
            raise ValueError('Process memory bounds')
        memory[stem] = row
    rows = []
    previous_end = -1
    for i in range(5):
        prefix = f's{i}.'
        need(prefix + 'frames', 32)
        start, end = wide(prefix + 'start'), wide(prefix + 'end')
        elapsed = num(prefix + 'elapsed_ms')
        phases = {n: wide(prefix + n) for n in ('render', 'upload', 'present')}
        if start < previous_end or end <= start or elapsed >= 30000:
            raise ValueError('Batch ordering/deadline')
        if sum(phases.values()) > end-start:
            raise ValueError('Phase durations exceed batch')
        batch_ms = (end-start)*1000/frequency
        if batch_ms >= 30000 or abs(batch_ms-elapsed) > 250 + elapsed*.20:
            raise ValueError('Counter/coarse-clock disagreement')
        rows.append(dict(stage=i, frames=32, elapsed_ms=elapsed, qpc_batch_ms=batch_ms,
                         **{n+'_ms': v*1000/frequency for n,v in phases.items()}))
        previous_end = end
    if {k for k in f if k.startswith('loop.')} != seen:
        raise ValueError('Unknown loop metadata')
    return dict(rows=rows, memory=memory, frequency=frequency, frames=160,
                commit_after_release_delta=memory['released']['commit']-memory['before']['commit'],
                scope='Checked batch endpoints; API phase latency, not scanout/FPS or leak freedom')


def validate(raw, *args):
    f = scene.scene.decode(raw)
    if f.get('schema') != 'xwn-scene-loop-1' or f.get('scope') != 'repeated-windowed-xyz-software-phase-costs':
        raise ValueError('Loop identity')
    cost = telemetry(f)
    base = {k:v for k,v in f.items() if not k.startswith('loop.')}
    base['schema'] = 'xwn-scene-present-2'
    base['scope'] = 'windowed-xyz-texture-depth-rgb-software'
    result = scene.validate(''.join(k+'='+v+'\r\n' for k,v in base.items()).encode(), *args)
    if not any(n.lower().endswith('\\psapi.dll') for n in result['modules']):
        raise ValueError('Missing live PSAPI module')
    result.update(telemetry=cost, scope=cost['scope'], sustained_frames=160)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('prefix', type=Path)
    p.add_argument('--backend', choices=('default','hel'), required=True)
    a = p.parse_args(); s = str(a.prefix)
    print(json.dumps(validate(Path(s+'.txt').read_bytes(),
        *[Path(s+'-'+n+'.bin').read_bytes() for n in scene.SUFFIXES],
        a.backend, int(Path(s+'.exit').read_text(encoding='utf-8'))), indent=2))


if __name__ == '__main__':
    main()
