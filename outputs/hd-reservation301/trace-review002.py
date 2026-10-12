"""Supplement closed cold audits with the existing actual miniport trace; no launch."""
import contextlib
import hashlib
import json
import struct
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
sys.path.insert(0, str(k.parent / 'video-text-oracle206'))
from common import ColdIO, readers, read, sha

dest = k / 'trace-review.json'
assert not dest.exists()
source = Path('/home/paul/xbox-windows-native/build/hd-reservation300-build001/source')
src = source / 'win32ss/drivers/miniport/xboxvmp/nt5'
pins = {n: sha(src / n) for n in ['video_trace.c', 'video_shared.c']}
rows = {}
for case, physical in [('control001', 0x03c00000), ('candidate001', 0x03700000)]:
    out = k / case
    assert read(out / 'closure.json')['closed']
    fixture = read(out / 'fixture.json')
    disk = Path('/mnt/d/xwn301/runs/nt5-hd301-' + case) / 'hdd.qcow2'
    captures = {}
    for phase, path in [('before', Path(fixture['fixture_path_linux'])), ('after', disk)]:
        target = out / 'artifacts' / (phase + '-video-trace.bin')
        assert not target.exists()
        with ColdIO(path) as io:
            blob = readers(io, path)['F'].read('winnt/system32/xwn-video-trace.bin')
        assert len(blob) == 4096 and blob[:16] == b'XWN-VID-TRACE01\n'
        target.write_bytes(blob)
        values = struct.unpack('<1024I', blob)
        count, lost = values[4:6]
        assert count <= 254
        events = [list(values[8 + i * 4:12 + i * 4]) for i in range(count)]
        captures[phase] = dict(sha256=hashlib.sha256(blob).hexdigest(), count=count,
                               lost=lost, saturated=count == 254, events=events)
    after = captures['after']
    acquisitions = [v for v in after['events'] if v[0] == 0x30]
    releases = [v for v in after['events'] if v[0] in (0x31, 0x32)]
    passed = (not after['lost'] and not after['saturated'] and bool(acquisitions)
              and all(v[1] == 0 and v[2] and v[2] % 4096 == 0 and v[3] == physical
                      for v in acquisitions)
              and all(v[1] == 0 for v in releases))
    rows[case] = dict(captures=captures, expected_physical=physical,
                      acquisitions=acquisitions, releases=releases, passed=passed)
result = dict(passed=all(v['passed'] for v in rows.values()), rows=rows,
              source_pins=pins, checker_sha256=sha(Path(__file__)),
              scope='Actual retained miniport acquire status, returned virtual address and physical base.',
              limits='Trace does not expose complete descriptor, PFN ownership, aliases or PTE cache bits. '
                     'Normal shutdown evidence comes from separate cold audits. No physical qualification.')
dest.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({c: {n: row[n] for n in ['passed', 'acquisitions', 'releases']}
                  for c, row in rows.items()}, indent=2))
