"""Add measured alias/path/capacity details without changing old continuation tail."""
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];p=ws/'outputs/engineering-notes/CONTINUATION.md';old=k.parent/'gpu-reference-pair242/artifacts/continuation-before242.md'
b=p.read_bytes();assert b.endswith(old.read_bytes());prefix=b[:-len(old.read_bytes())].decode('utf-8');assert 'Modeled texture alias' not in prefix
note='''Modeled texture alias exactly overlaps retained color surface65208320/1228800;
all model refs unchanged after readback. Directory capture has no missing
baseline path; generated wmiadap.log present in239/241 but absent in242/243,
cause unproved. Records retained, no all-file-content or power-loss claim.
Final closed243 portable offload readback/original-path verification restores C
above20GiB; next build/portable projection still needs explicit capacity check.

'''
p.write_bytes(prefix.encode('utf-8')+note.encode('utf-8')+old.read_bytes())
print('243 final measured continuation details appended')
