# SPDX-License-Identifier: MIT
"""Host-only immutable image extent contract. No disk/device access or NTFS code.

The caller's allocation/owner scan and identity values are MODELED authority;
an eventual loader/driver must independently derive them from the real medium.
"""
from dataclasses import dataclass
import hashlib
import json

SECTOR = 512
U64 = (1 << 64) - 1
MAX_FILE = 0xfffffe00  # Largest sector-aligned FATX 32-bit file length.
MAX_CLUSTERS = 262144
MAX_REQUEST = 1024 * 1024


class Refusal(ValueError):
    pass


def integer(n, lo, hi):
    if type(n) is not int or not lo <= n <= hi:
        raise Refusal('integer bound/type')
    return n


@dataclass(frozen=True)
class Geometry:
    disk_bytes: int
    partition_start: int
    partition_bytes: int
    data_offset: int
    cluster_bytes: int
    cluster_count: int

    def validate(self):
        for n in (self.disk_bytes, self.partition_start, self.partition_bytes,
                  self.data_offset, self.cluster_bytes):
            integer(n, 0, U64)
            if n % SECTOR:
                raise Refusal('unaligned geometry')
        if self.cluster_bytes not in (512, 1024, 2048, 4096, 8192, 16384,
                                      32768, 65536):
            raise Refusal('cluster size')
        integer(self.cluster_count, 1, (1 << 32) - 2)
        if (self.partition_start == 0 or self.data_offset == 0 or
            self.partition_start + self.partition_bytes > self.disk_bytes or
            self.data_offset + self.cluster_count * self.cluster_bytes >
                self.partition_bytes):
            raise Refusal('geometry containment')


@dataclass(frozen=True)
class ExtentMap:
    geometry: Geometry
    size: int
    # Tuple of absolute physical cluster starts, in logical file order.
    starts: tuple

    def segments(self, offset, count):
        integer(offset, 0, U64)
        integer(count, 1, MAX_REQUEST)
        if offset % SECTOR or count % SECTOR or offset + count > self.size:
            raise Refusal('request alignment/EOF')
        result = []
        pos = offset
        end = offset + count
        while pos < end:
            index, within = divmod(pos, self.geometry.cluster_bytes)
            n = min(end - pos, self.geometry.cluster_bytes - within)
            result.append((self.starts[index] + within, n))
            pos += n
        return tuple(result)


def make_map(g, size, chain, owners):
    """owners lists *all* observed owner identities for each allocated cluster.

    Cluster numbering here is explicitly 1..cluster_count. A real adapter must
    prove the matching FATX origin; this model does not parse an on-disk FAT.
    """
    g.validate()
    integer(size, SECTOR, MAX_FILE)
    if size % SECTOR or type(chain) is not tuple:
        raise Refusal('size/immutable chain')
    expected = (size + g.cluster_bytes - 1) // g.cluster_bytes
    if not 1 <= expected <= MAX_CLUSTERS or len(chain) != expected:
        raise Refusal('chain length/capacity')
    seen = set()
    starts = []
    for c in chain:
        integer(c, 1, g.cluster_count)
        if c in seen or owners.get(c) != ('image',):
            raise Refusal('cycle/crosslink/unknown owner')
        seen.add(c)
        starts.append(g.partition_start + g.data_offset +
                      (c - 1) * g.cluster_bytes)
    return ExtentMap(g, size, tuple(starts))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=True).encode('ascii')


def descriptor(mapping, disk_id, volume_serial):
    # Both are synthetic independently observed identity scalars in this model.
    integer(disk_id, 1, U64)
    integer(volume_serial, 1, U64)
    g = mapping.geometry
    payload = dict(version=1, disk_id=disk_id, volume_serial=volume_serial,
                   geometry=[g.disk_bytes, g.partition_start, g.partition_bytes,
                             g.data_offset, g.cluster_bytes, g.cluster_count],
                   size=mapping.size, starts=list(mapping.starts))
    raw = canonical(payload)
    return canonical(dict(payload=payload, sha256=hashlib.sha256(raw).hexdigest()))


def activate(raw, observed_map, disk_id, volume_serial):
    """Compare to a fresh independent scan, never trust saved physical offsets.

    Exact canonical comparison rejects partial publication and unknown fields.
    Digest is corruption detection, NOT authentication/anti-rollback security.
    """
    if type(raw) is not bytes or len(raw) > 8 * 1024 * 1024:
        raise Refusal('descriptor capacity/type')
    if raw != descriptor(observed_map, disk_id, volume_serial):
        raise Refusal('incomplete/unknown/stale descriptor or identity')
    return Session(observed_map)


class Session:
    """Sequential lifecycle model, not a concurrent NT driver implementation.

    Actual filesystem exclusion, nonpaged metadata, IRPs, lower completion and
    hardware cache flushing remain unimplemented. Failed sessions retain pins.
    """
    def __init__(self, mapping):
        self.mapping = mapping
        self.state = 'active'
        self.pinned = True
        self.dirty = False

    def transfer(self, offset, count, lower, write=False):
        if self.state != 'active' or type(write) is not bool:
            raise Refusal('session inactive/operation type')
        parts = self.mapping.segments(offset, count)  # Validate all before IO.
        completed = 0
        for physical, length in parts:
            if write:
                self.dirty = True  # A failed/short lower write may mutate media.
            try:
                n = lower(physical, length, write)
            except Exception:
                self.state = 'quarantined'
                raise
            if type(n) is not int or n != length:
                self.state = 'quarantined'
                raise Refusal(f'lower incomplete; prior completed={completed}')
            completed += n
        return completed

    def flush(self, lower_flush):
        if self.state != 'active':
            raise Refusal('session inactive')
        try:
            if lower_flush() is not True:
                raise Refusal('lower flush failed')
        except Exception:
            self.state = 'quarantined'
            raise
        self.dirty = False

    def close(self, lower_flush):
        self.flush(lower_flush)
        self.state = 'closed'
        self.pinned = False
