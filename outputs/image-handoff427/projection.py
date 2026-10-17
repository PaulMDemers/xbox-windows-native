# SPDX-License-Identifier: MIT
"""Host-only contiguous image partition contract; no native hooks or disk writes.

Geometry, chain ownership and NTFS serial come from a MODELED independent scan.
The 512-byte experimental envelope is not an installed on-disk format.
"""
from dataclasses import dataclass, replace
import hashlib
import struct

SECTOR = 512
PREFIX = 65536
MAX_FILE = 0xfffffe00
U64 = (1 << 64) - 1
MAGIC = b'XWN427\0\0'
FMT = '<8sIIII16s8Q'
BODY = struct.calcsize(FMT)


class Refusal(ValueError):
    pass


def uint(n, low, high):
    if type(n) is not int or not low <= n <= high:
        raise Refusal('integer type/bound')
    return n


@dataclass(frozen=True)
class Header:
    identity: bytes
    disk_bytes: int
    parent_start: int
    parent_bytes: int
    file_start: int
    file_bytes: int
    inner_offset: int
    inner_bytes: int
    ntfs_serial: int

    def validate(self):
        if type(self.identity) is not bytes or len(self.identity) != 16 or not any(self.identity):
            raise Refusal('image identity')
        for n in (self.disk_bytes, self.parent_start, self.parent_bytes,
                  self.file_start, self.file_bytes, self.inner_offset, self.inner_bytes):
            uint(n, SECTOR, U64)
            if n % SECTOR:
                raise Refusal('alignment')
        uint(self.ntfs_serial, 1, U64)
        if (self.file_bytes > MAX_FILE or self.inner_offset != PREFIX or
            self.inner_offset + self.inner_bytes != self.file_bytes or
            self.parent_start + self.parent_bytes > self.disk_bytes or
            self.file_start < self.parent_start or
            self.file_start + self.file_bytes > self.parent_start + self.parent_bytes or
            (self.file_start + self.inner_offset) // SECTOR > 0xffffffff):
            raise Refusal('containment/format bounds')

    def encode(self):
        self.validate()
        head = struct.pack(FMT, MAGIC, 1, SECTOR, 0, 0, self.identity,
                           self.disk_bytes, self.parent_start, self.parent_bytes,
                           self.file_start, self.file_bytes, self.inner_offset,
                           self.inner_bytes, self.ntfs_serial)
        body = head + bytes(SECTOR - 32 - len(head))
        return body + hashlib.sha256(body).digest()


def decode(raw, expected_id):
    if type(raw) is not bytes or len(raw) != SECTOR:
        raise Refusal('header length/type')
    if hashlib.sha256(raw[:-32]).digest() != raw[-32:]:
        raise Refusal('header integrity')
    values = struct.unpack_from(FMT, raw)
    if values[:5] != (MAGIC, 1, SECTOR, 0, 0) or any(raw[BODY:-32]):
        raise Refusal('unsupported header/reserved bits')
    if values[5] != expected_id or type(expected_id) is not bytes:
        raise Refusal('launch identity mismatch')
    h = Header(values[5], *values[6:])
    h.validate()
    return h


@dataclass(frozen=True)
class Partition:
    number: int
    start: int
    size: int
    kind: int


def project(h, partitions, mapping, actual_serial):
    """mapping is a validated426 ExtentMap from a complete supplied owner scan.

    No actual FAT scanner, loader or Windows storage authority is implemented.
    Replace only partition1; no extra enclosing E partition is published.
    """
    h.validate()
    if type(partitions) is not tuple or not 2 <= len(partitions) <= 16:
        raise Refusal('layout container/capacity')
    if tuple(p.number for p in partitions) != tuple(range(1, len(partitions)+1)):
        raise Refusal('partition ordinal mismatch')
    seen = set()
    ranges = []
    for p in partitions:
        uint(p.number, 1, 16)
        uint(p.start, SECTOR, h.disk_bytes)
        uint(p.size, SECTOR, h.disk_bytes)
        uint(p.kind, 1, 255)
        if (p.start % SECTOR or p.size % SECTOR or p.number in seen or
            p.start + p.size > h.disk_bytes):
            raise Refusal('partition geometry/identity')
        seen.add(p.number)
        ranges.append((p.start, p.start+p.size))
    ordered = sorted(ranges)
    if any(a[1] > b[0] for a, b in zip(ordered, ordered[1:])):
        raise Refusal('overlapping source partitions')
    by_id = {p.number: p for p in partitions}
    if 1 not in by_id or 2 not in by_id:
        raise Refusal('missing E/C identity')
    parent = by_id[1]
    if (parent.start, parent.size, parent.kind) != (h.parent_start, h.parent_bytes, 0x0b):
        raise Refusal('parent E mismatch')
    g = mapping.geometry
    if (g.disk_bytes, g.partition_start, g.partition_bytes, mapping.size) != (
            h.disk_bytes, h.parent_start, h.parent_bytes, h.file_bytes):
        raise Refusal('independent map mismatch')
    expected_count = (h.file_bytes + g.cluster_bytes - 1) // g.cluster_bytes
    if len(mapping.starts) != expected_count or not mapping.starts:
        raise Refusal('incomplete map')
    if mapping.starts[0] != h.file_start:
        raise Refusal('relocated/replaced image')
    if any(b != a + g.cluster_bytes for a, b in zip(mapping.starts, mapping.starts[1:])):
        raise Refusal('fragmented image unsupported')
    uint(actual_serial, 1, U64)
    if actual_serial != h.ntfs_serial:
        raise Refusal('NTFS identity mismatch')
    inner = Partition(1, h.file_start + PREFIX, h.inner_bytes, 0x07)
    return tuple(inner if p.number == 1 else p for p in partitions)


class ReadOnlyView:
    """Bounded real byte-reader adapter; supplied lower reader is never written.

    No NTFS parser or FAT scanner. This view is for a later read-only oracle,
    not proof that the future HAL/loader will enforce the same contract.
    """
    def __init__(self, projected, lower_read):
        self.partition = next(p for p in projected if p.number == 1)
        self.read = lower_read
        self.failed = False

    def read_at(self, offset, count):
        if self.failed:
            raise Refusal('reader quarantined')
        uint(offset, 0, U64)
        uint(count, 1, 65536)
        if offset % SECTOR or count % SECTOR or offset+count > self.partition.size:
            raise Refusal('read bounds')
        try:
            data = self.read(self.partition.start + offset, count)
            if type(data) is not bytes or len(data) != count:
                raise Refusal('short/invalid lower read')
        except Exception:
            self.failed = True
            raise
        return data
