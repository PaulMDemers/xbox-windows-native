"""Verify saved raw log context and correction to the older non-ASCII byte count."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;r=json.loads((k/'context-review.json').read_text())
inputs=[('control',k.parent/'fatx-first-install-0101/001/artifacts/after-setupapi.log'),('physical_after',k.parent/'physical-gpu-setup/artifacts/after-setupapi.log'),('physical_before',k.parent/'physical-gpu-setup/artifacts/before-setupapi.log')]
data={}
for label,path in inputs:
 data[label]=path.read_bytes();assert hashlib.sha256(data[label]).hexdigest()==r[label+'_sha256']
physical=data['physical_after'];control=data['control'];off=r['physical_malformed_offset'];cp=r['control_warning_offset']
assert physical.startswith(data['physical_before']) and len(data['physical_before'])==r['physical_before_bytes']
assert physical[:off].splitlines()[-1].decode('ascii')==r['physical_preceding_line']
assert control[:cp].splitlines()[-1].decode('ascii')==r['control_preceding_line']
span=physical[off:off+111]
a=json.loads((k.parent/'physical-gpu-setup/log-anomaly.json').read_text());assert span.hex()==a['malformed_range_hex']
assert sum(x>127 for x in span)==r['physical_prefix_non_ascii_bytes']==91
assert span.count(127)==r['physical_prefix_del_count']==1
assert sum(not(32<=x<=126 or x in [9,10,13]) for x in span)==r['physical_prefix_nontext_count']==92
assert off-cp==r['padding_bytes']==131059
print('Preserved raw context and byte-count clarification verified; no physical access.')
