"""Reuse the identical concurrency workload and cold gates for candidate0100."""
from pathlib import Path
k=Path(__file__).resolve().parent;prior=k.parent/'fatx-cleanup-order'
for name in ['prepare-test-tools.py','review-binary.py','prepare-layouts.py']:
    p=k/name;assert not p.exists()
    p.write_text((prior/name).read_text().replace('fatx-cleanup-order','fatx-namespace-order').replace('0099','0100'))
