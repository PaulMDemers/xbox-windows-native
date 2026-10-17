# SPDX-License-Identifier: MIT
"""Additional bounded EOF, guard-content, maximum-size and error-path tests."""
from pathlib import Path
import hashlib
import json
from model import Geometry, make_map, descriptor, activate, Refusal, MAX_FILE

root = Path(__file__).resolve().parent
out = root / 'tests002.json'
if out.exists():
    raise SystemExit('Consumed attempt')
checks = 0


def check(value):
    global checks
    assert value
    checks += 1


# Separate small byte-array medium; expected writes computed per byte from the
# original cluster sequence, never by calling segments to construct the oracle.
g = Geometry(131072, 32768, 65536, 4096, 4096, 15)
chain = (7, 2, 9)
size = 12288 - 512
m = make_map(g, size, chain, {c: ('image',) for c in chain})
raw = descriptor(m, 426, 555)
for start, count in [(0, 512), (3584, 1024), (4096, 7680), (0, size),
                     (size - 512, 512)]:
    disk = bytearray((i * 17 + 9) & 255 for i in range(g.disk_bytes))
    expected = disk.copy()
    payload = bytes((i * 31 + 7) & 255 for i in range(count))
    for i, b in enumerate(payload):
        logical = start + i
        physical = 32768 + 4096 + (chain[logical // 4096] - 1) * 4096 + logical % 4096
        expected[physical] = b
    cursor = [0]
    def write(p, n, is_write):
        check(is_write)
        disk[p:p+n] = payload[cursor[0]:cursor[0]+n]
        cursor[0] += n
        return n
    s = activate(raw, m, 426, 555)
    s.transfer(start, count, write, True)
    check(disk == expected)  # Includes every unrelated byte and final slack.
    check(cursor[0] == count)
    s.close(lambda: True)

# Maximum format length, fragmented last cluster and exact last sector.
large = Geometry(1 << 40, 1 << 38, 1 << 34, 65536, 65536, 100000)
ch = tuple(range(1, 65537))
lm = make_map(large, MAX_FILE, ch, {c: ('image',) for c in ch})
check(lm.segments(MAX_FILE - 512, 512) ==
      ((large.partition_start + large.data_offset + MAX_FILE - 512, 512),))
check(lm.segments(65536 - 512, 1024) ==
      ((large.partition_start + large.data_offset + 65536 - 512, 512),
       (large.partition_start + large.data_offset + 65536, 512)))

for write in (False, True):
    s = activate(raw, m, 426, 555)
    def fail(*args):
        raise OSError('injected')
    try:
        s.transfer(0, 512, fail, write)
    except OSError:
        pass
    else:
        raise AssertionError('lower error swallowed')
    check(s.pinned and s.state == 'quarantined' and s.dirty == write)
s = activate(raw, m, 426, 555)
try:
    s.close(fail)
except OSError:
    pass
else:
    raise AssertionError('flush error swallowed')
check(s.state == 'quarantined' and s.pinned)

result = dict(passed=True, checks=checks,
              scope='synthetic byte-array guards, format bound and lower-error model',
              actual_device_io=False, inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (root / 'model.py', Path(__file__))})
with out.open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
