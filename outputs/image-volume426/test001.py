# SPDX-License-Identifier: MIT
"""Bounded synthetic tests; no actual FATX/NTFS/device contents accessed."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
from model import (Geometry, make_map, descriptor, activate, Refusal,
                   MAX_FILE, MAX_CLUSTERS, U64)

root = Path(__file__).resolve().parent
out = root / 'tests001.json'
if out.exists():
    raise SystemExit('Consumed attempt: choose new test ID')
checks = {}


def check(group, value):
    assert value, group
    checks[group] = checks.get(group, 0) + 1


def refused(group, fn):
    try:
        fn()
    except Refusal:
        check(group, True)
    else:
        raise AssertionError(group)


# Independent sector-list oracle, not the production segments implementation.
g = Geometry(1 << 40, (1 << 37) + 4096, 1 << 30, 65536, 4096, 200000)
chain = (9, 2, 17, 4, 18, 19, 7)
owners = {c: ('image',) for c in chain}
size = 7 * 4096 - 512
m = make_map(g, size, chain, owners)
oracle = [g.partition_start + g.data_offset + (c - 1) * 4096 + s * 512
          for c in chain for s in range(8)][:size // 512]
for first in range(len(oracle)):
    for count in range(1, len(oracle) - first + 1):
        parts = m.segments(first * 512, count * 512)
        actual = [p + i for p, n in parts for i in range(0, n, 512)]
        check('every_sector_range', actual == oracle[first:first + count])
        check('high_lba_no_28bit_wrap', all(p >= 1 << 37 for p in actual))

rng = random.Random(426)
for _ in range(200):
    ch = tuple(rng.sample(range(1, 200001), rng.randint(1, 32)))
    mapping = make_map(g, len(ch) * 4096, ch, {c: ('image',) for c in ch})
    a = rng.randrange(len(ch) * 8)
    n = rng.randint(1, len(ch) * 8 - a)
    expected = [g.partition_start + g.data_offset + (ch[k // 8] - 1) * 4096
                + (k % 8) * 512 for k in range(a, a + n)]
    actual = [p + j for p, length in mapping.segments(a * 512, n * 512)
              for j in range(0, length, 512)]
    check('random_fragmentation', actual == expected)

for offset, count in [(-512, 512), (0, 0), (1, 512), (0, 513),
                      (size, 512), (size - 512, 1024), (U64, 512),
                      (False, 512), (0, 1049088)]:
    refused('bad_requests', lambda: m.segments(offset, count))
for changes in [dict(partition_start=0), dict(data_offset=0),
                dict(cluster_bytes=3000), dict(cluster_count=True),
                dict(partition_bytes=512), dict(disk_bytes=4096),
                dict(partition_start=U64), dict(cluster_count=0),
                dict(data_offset=U64 - 511)]:
    refused('bad_geometry', lambda: make_map(replace(g, **changes), size, chain, owners))
for bad in [chain[:-1], chain + (20,), (9, 2, 17, 4, 18, 19, 9),
            (0,) + chain[1:], (200001,) + chain[1:], (True,) + chain[1:]]:
    refused('bad_chain', lambda: make_map(g, size, bad, owners))
for badowner in [(), ('other',), ('image', 'other'), ('image', 'image')]:
    bad = dict(owners)
    bad[2] = badowner
    refused('bad_owner', lambda: make_map(g, size, chain, bad))
for length in [0, -1, 513, MAX_FILE + 512, True]:
    refused('bad_file_size', lambda: make_map(g, length, chain, owners))
small = replace(g, cluster_bytes=512, cluster_count=1000000)
refused('bounded_allocation', lambda: make_map(small, (MAX_CLUSTERS + 1) * 512,
                                             (), {}))

# Incomplete publication: no shorter prefix activates, even if old data remains.
raw = descriptor(m, 426, 12345)
for length in range(len(raw)):
    refused('torn_descriptor_prefix', lambda: activate(raw[:length], m, 426, 12345))
for index in range(len(raw)):
    changed = bytearray(raw)
    changed[index] ^= 1
    refused('descriptor_bit_mutation', lambda: activate(bytes(changed), m, 426, 12345))
for altered in [raw + b' ', raw + raw, b'', b'{}']:
    refused('descriptor_transport', lambda: activate(altered, m, 426, 12345))
for disk, vol in [(427, 12345), (426, 12346), (True, 12345), (426, 0)]:
    refused('identity_mismatch', lambda: activate(raw, m, disk, vol))
newchain = chain[::-1]
changedmap = make_map(g, size, newchain, owners)
refused('external_relocation', lambda: activate(raw, changedmap, 426, 12345))
refused('external_resize', lambda: activate(raw, make_map(g, size - 512, chain, owners),
                                         426, 12345))

# Short transfers/exceptions are never successful and retain pinned mapping.
for fail_index in range(len(chain)):
    for failure in ('short', 'exception', 'bool'):
        session = activate(raw, m, 426, 12345)
        calls = []
        def lower(p, n, write):
            calls.append((p, n))
            if len(calls) - 1 == fail_index:
                if failure == 'exception':
                    raise OSError('injected lower failure')
                return True if failure == 'bool' else n - 512
            return n
        try:
            session.transfer(0, size, lower, True)
        except (Refusal, OSError):
            pass
        else:
            raise AssertionError('failed write succeeded')
        check('partial_write_quarantine', session.state == 'quarantined' and
              session.pinned and session.dirty and len(calls) == fail_index + 1)
        refused('quarantine_no_resume', lambda: session.transfer(0, 512, lower))
        refused('quarantine_no_unpin', lambda: session.close(lambda: True))

for result in (False, None, 1):
    s = activate(raw, m, 426, 12345)
    s.transfer(0, 512, lambda p, n, w: n, True)
    refused('flush_no_fake_success', lambda: s.close(lambda: result))
    check('failed_flush_keeps_pin', s.pinned and s.dirty and s.state == 'quarantined')

s = activate(raw, m, 426, 12345)
calls = []
refused('invalid_before_io', lambda: s.transfer(size - 512, 1024,
                                               lambda *args: calls.append(args), True))
check('invalid_no_mutation', calls == [] and not s.dirty)
check('full_transfer', s.transfer(0, size, lambda p, n, w: n, True) == size)
s.close(lambda: True)
check('successful_close', not s.pinned and not s.dirty and s.state == 'closed')
refused('closed_no_io', lambda: s.transfer(0, 512, lambda p, n, w: n))
check('restart_revalidates', activate(raw, m, 426, 12345).state == 'active')

result = dict(scope='synthetic host extent/lifecycle model only', passed=True,
              checks=checks, total=sum(checks.values()), native_build=False,
              driver_or_guest_test=False, real_flush_or_crash_recovery=False,
              inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (root / 'model.py', Path(__file__))})
with out.open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
