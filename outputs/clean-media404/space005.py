"""Reserve 20 GiB plus measured sparse RAW upper bound and extraction budget."""
import hashlib, json, subprocess
from pathlib import Path
from build_space import require_space

def preflight(p):
    disk = p / 'disk.qcow2'
    info = json.loads(subprocess.check_output(['qemu-img', 'info', '--output=json', str(disk)]))
    assert info['virtual-size'] == 2 * 1024**3 and not info.get('backing-filename')
    data = subprocess.check_output(['qemu-img', 'map', '--output=json', str(disk)])
    rows = json.loads(data); cursor = 0; allocated = 0
    for row in rows:
        assert row['depth'] == 0 and row['start'] == cursor and row['length'] > 0
        cursor += row['length']
        if row['data']:
            allocated += row['length']
        else:
            assert row['zero']
    assert cursor == info['virtual-size']
    budget = 256 * 1024**2
    result = require_space(p, minimum_gib=20 + (allocated + budget) / 1024**3)
    result.update(reserve_bytes=20 * 1024**3, sparse_raw_allocated_upper_bound=allocated,
                  extraction_and_metadata_budget=budget, map_sha256=hashlib.sha256(data).hexdigest(),
                  reason='Explicit sparse conversion skips unallocated zero extents; 20 GiB reserve unchanged')
    dest = Path(__file__).parent / 'cold-space005.json'
    with dest.open('x') as f:
        json.dump(result, f, indent=2)
    return result
