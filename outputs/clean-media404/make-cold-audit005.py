import json
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K/'cold-audit004.py').read_text()
s=s.replace('space = require_space(P, minimum_gib=22.5)', 'from space005 import preflight\n        space = preflight(P)')
s=s.replace("['qemu-img', 'convert', '-O', 'raw'", "['qemu-img', 'convert', '-S', '4k', '-O', 'raw'")
s=s.replace("    records = {name:", "    assert raw.stat().st_blocks * 512 <= space['sparse_raw_allocated_upper_bound']\n    assert sum(p.stat().st_size for p in paths.values()) < space['extraction_and_metadata_budget']\n    records = {name:")
s=s.replace("    report['raw_copy_removed_after_verified_extraction'] = True", "    report['raw_copy_removed_after_verified_extraction'] = True\n    report['final_space'] = require_space(P)")
with (K/'cold-audit005.py').open('x') as f:f.write(s)
with (K/'cold-audit004-phase04-refusal.json').open('x') as f:
    json.dump(dict(phase=4, refused_before_conversion_or_extraction=True,
        free_bytes=23410987008, requested_bytes=24159191040,
        reason='Conservative full virtual RAW plus 512 MiB projection; WSL freed RAW extents did not immediately return host capacity',
        replacement='005 retains 20 GiB plus full measured data extents and 256 MiB extraction/metadata budget; explicit sparse conversion and actual allocation assertions'),f,indent=2)
