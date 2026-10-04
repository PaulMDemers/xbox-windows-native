"""Validate the reported F: extent without trusting virtualized C: offsets.

This produces a planning contract, never a disk-write authorization. The source
is Xbox-kernel query output, not an on-disk partition table or Windows I/O proof.
"""
from pathlib import Path
import hashlib
import json
import re


def analyze(text):
    if 'INVENTORY_COMPLETE log_ok=1' not in text:
        raise ValueError('Inventory incomplete or log failed')
    if set(map(int, re.findall(r'^END partition=(\d+)\s*$', text, re.M))) != set(range(8)):
        raise ValueError('Missing partition query results')
    parts = {}
    for number, start, length in re.findall(
            r'^partition=(\d+) start_bytes=(\d+) length_bytes=(\d+)', text, re.M):
        number, start, length = map(int, (number, start, length))
        if number in parts:
            raise ValueError('Duplicate partition data')
        parts[number] = (start, length)
    if 0 not in parts or parts[0][0] != 0 or parts[0][1] <= 0:
        raise ValueError('Missing whole-disk extent')
    disk_bytes = parts[0][1]
    if disk_bytes % 512:
        raise ValueError('Whole-disk extent not sector aligned')
    if 6 not in parts:
        raise ValueError('F partition query did not succeed')
    start, length = parts[6]
    if start < 512 or length <= 0 or start % 512 or length % 512:
        raise ValueError('Invalid F extent')
    if start >= disk_bytes or length > disk_bytes - start:
        raise ValueError('F extent exceeds physical disk')
    excluded = []
    for number, (other_start, other_length) in parts.items():
        if number in (0, 6):
            continue
        if other_start < 0 or other_length <= 0 or other_start + other_length > disk_bytes:
            # Keep this explicit: a softmod query can describe a virtual volume.
            excluded.append(number)
            continue
        if start < other_start + other_length and other_start < start + length:
            raise ValueError('F overlaps another in-bounds reported partition')
    rows = re.findall(
        r'^volume=6 total_units=(\d+) free_units=(\d+) sectors_per_unit=(\d+) bytes_per_sector=(\d+)',
        text, re.M)
    if len(rows) != 1:
        raise ValueError('Missing or duplicate F space information')
    total, free, sectors, size = map(int, rows[0])
    if size != 512 or sectors == 0 or sectors & (sectors - 1):
        raise ValueError('Unsupported sector or cluster geometry')
    cluster = size * sectors
    if total <= 0 or free > total or total * cluster > length:
        raise ValueError('Invalid volume allocation counts')
    return {
        'source_scope': 'Xbox-kernel queries; not raw partition-table verification',
        'disk_bytes': disk_bytes, 'disk_sectors': disk_bytes // 512,
        'target_drive': 'F:', 'partition_number': 6,
        'start_bytes': start, 'length_bytes': length,
        'start_lba': start // 512, 'sector_count': length // 512,
        'end_lba_exclusive': (start + length) // 512,
        'cluster_bytes': cluster, 'volume_data_bytes': total * cluster,
        'free_bytes': free * cluster, 'free_gib': free * cluster / 2**30,
        'requires_addressing_beyond_lba28': (start + length) // 512 > (1 << 28),
        'excluded_out_of_disk_query_partitions': excluded,
        'raw_partition_table_verified': False,
        'native_windows_f_partition_supported': False,
        'native_windows_large_lba_io_verified': False,
        'native_windows_writes_ready': False,
    }


if __name__ == '__main__':
    kit = Path(__file__).resolve().parent
    data = (kit/'evidence/physical-storage.txt').read_bytes()
    result = analyze(data.decode())
    result['input_sha256'] = hashlib.sha256(data).hexdigest()
    retrieval = json.loads((kit/'physical-retrieval.json').read_text())
    assert retrieval['sha256'] == result['input_sha256']
    (kit/'physical-layout.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
