# SPDX-License-Identifier: MIT
"""Synthetic media and partition-contract checks; never writes a real device."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import struct
import sys
from projection import Header, Partition, project, decode, ReadOnlyView, Refusal, PREFIX, MAX_FILE

K = Path(__file__).resolve().parent
prior = K.parent/'image-volume426/model.py'
assert hashlib.sha256(prior.read_bytes()).hexdigest() == 'e12845f036fa1989c386138f2879d2af6d546d177ef312b85cd56686186833c3'
sys.path.insert(0, str(prior.parent))
from model import Geometry, make_map
out = K/'tests001.json'
assert not out.exists()
counts = {}
def check(group, value):
    assert value, group
    counts[group] = counts.get(group, 0) + 1
def reject(group, fn):
    try:
        fn()
    except Refusal:
        check(group, True)
    else:
        raise AssertionError(group)

g = Geometry(1 << 40, 1 << 37, 1 << 30, 65536, 4096, 200000)
chain = tuple(range(101, 133))
m = make_map(g, 131072, chain, {c: ('image',) for c in chain})
h = Header(bytes(range(16)), g.disk_bytes, g.partition_start, g.partition_bytes,
           m.starts[0], m.size, PREFIX, 65536, 427)
layout = (Partition(1, g.partition_start, g.partition_bytes, 0x0b),
          Partition(2, 1048576, 52428800, 6),
          Partition(3, 104857600, 52428800, 6))
raw = h.encode()
check('header_roundtrip', decode(raw, h.identity) == h)
projected = project(h, layout, m, 427)
check('only_E_replaced', projected[1:] == layout[1:])
check('parent_E_not_exposed', not any(p.start == h.parent_start for p in projected))
check('inner_exact', projected[0] == Partition(1, h.file_start+PREFIX, 65536, 7))
check('immutable_inputs', layout[0].start == g.partition_start and m.starts[0] == h.file_start)

for i in range(512):
    reject('every_short_header', lambda: decode(raw[:i], h.identity))
    for bit in range(8):
        b = bytearray(raw)
        b[i] ^= 1 << bit
        reject('every_single_bit', lambda: decode(bytes(b), h.identity))
reject('oversized_header', lambda: decode(raw+b'X', h.identity))
reject('wrong_launch_id', lambda: decode(raw, bytes(range(1, 17))))
# Recomputed digests cannot hide forbidden format fields; digest is not auth.
for pos in [8, 12, 16, 20, 104, 479]:
    b = bytearray(raw)
    b[pos] ^= 1
    b[-32:] = hashlib.sha256(b[:-32]).digest()
    reject('semantic_header_mutations', lambda: decode(bytes(b), h.identity))

for changes in [dict(identity=bytes(16)), dict(inner_offset=512),
                dict(file_bytes=MAX_FILE+512), dict(inner_bytes=65535),
                dict(parent_start=0), dict(parent_bytes=512),
                dict(disk_bytes=1024), dict(ntfs_serial=True),
                dict(file_start=h.parent_start-512)]:
    reject('invalid_header_geometry', lambda: replace(h, **changes).encode())
for changes in [dict(file_start=h.file_start+4096), dict(ntfs_serial=428),
                dict(file_bytes=h.file_bytes-512, inner_bytes=h.inner_bytes-512),
                dict(parent_start=h.parent_start-512, parent_bytes=h.parent_bytes+512)]:
    mutated = replace(h, **changes)
    # These are structurally encodable, but mismatch independent media facts.
    valid = decode(mutated.encode(), h.identity)
    reject('stale_or_forged_media_facts', lambda: project(valid, layout, m, 427))

badlayouts = [(), layout[:1], layout[::-1], (layout[0], layout[0]),
              (layout[0], replace(layout[1], start=h.file_start)),
              (replace(layout[0], kind=7), *layout[1:]),
              (layout[0], replace(layout[1], size=True), layout[2]),
              (layout[0], replace(layout[1], start=g.disk_bytes), layout[2])]
for bad in badlayouts:
    reject('layout_identity_or_overlap', lambda: project(h, bad, m, 427))
ch = chain[:-2] + (chain[-1], chain[-2])
fragmented = make_map(g, m.size, ch, {c: ('image',) for c in ch})
reject('fragmentation_no_fallback', lambda: project(h, layout, fragmented, 427))
reject('serial_mismatch', lambda: project(h, layout, m, 428))

# Sparse synthetic byte oracle: whole image and parent stay virtual, no big file.
# Different byte values before prefix/inside/after make incorrect offsets visible.
calls = []
def reader(start, count):
    calls.append((start, count))
    return bytes(((i - h.file_start) * 13 + ((i-h.file_start) >> 8)) & 255
                 for i in range(start, start+count))
view = ReadOnlyView(projected, reader)
for offset in range(0, h.inner_bytes, 512):
    expected = bytes(((i+PREFIX)*13 + ((i+PREFIX) >> 8)) & 255
                     for i in range(offset, offset+512))
    check('independent_byte_reads', view.read_at(offset, 512) == expected)
    check('high_LBA_prefix_protection', calls[-1] == (h.file_start+PREFIX+offset, 512))
before = len(calls)
for offset, size in [(-512, 512), (1, 512), (0, 0), (0, 513),
                     (h.inner_bytes, 512), (h.inner_bytes-512, 1024),
                     (0, 65536+512), (True, 512)]:
    reject('invalid_view_request', lambda: view.read_at(offset, size))
check('invalid_request_no_IO', len(calls) == before)
for result in [b'', bytearray(512), None]:
    short = ReadOnlyView(projected, lambda p, n: result)
    reject('short_read', lambda: short.read_at(0, 512))
    check('short_read_quarantined', short.failed)
    reject('no_retry_after_short', lambda: short.read_at(0, 512))

# Loader/HAL agreement modeled as separately derived immutable projections.
second = project(decode(raw, h.identity), tuple(layout), make_map(
    g, m.size, tuple(chain), {c: ('image',) for c in chain}), 427)
check('independent_projection_agrees', second == projected)
check('header_or_map_not_written', raw == h.encode() and len(calls) == 128)

# Correct PDB rule: signature equality, PDB age >= image, DBI age exactly image.
def pdb_ok(sig, pdb_age, dbi_age, expected_sig, image_age):
    return sig == expected_sig and pdb_age >= image_age and dbi_age == image_age
for sig in (10, 11):
    for pa in range(4):
        for da in range(4):
            check('pdb_identity_age_cases', pdb_ok(sig, pa, da, 10, 1) ==
                  (sig == 10 and pa in (1,2,3) and da == 1))
result = dict(passed=True, scope='Synthetic host partition projection and read-only view',
              checks=counts, total=sum(counts.values()),
              native_or_guest_test=False, actual_fat_scan=False,
              actual_partition_exclusion=False,
              inputs={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [K/'projection.py', Path(__file__), prior]})
with out.open('x', encoding='utf-8', newline='\n') as f:
    f.write(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
