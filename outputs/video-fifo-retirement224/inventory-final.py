"""Pin the final external-constant table and derived bridge before build001."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'inventory-final.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((k/'inventory.json').read_text());assert prior['passed']
t=(k/'retirement.c').read_text();table=t[t.index('X224Offsets'):t.index('void x224_sample')]
assert [int(s,16) for s in re.findall(r'0x[0-9a-fA-F]+',table)]==[r['offset'] for r in prior['offsets']]
der=json.loads((k/'derivation.json').read_text())
assert all(sha(k/n)==h for n,h in der['derived'].items())
for n in ['context.c','context.h']:assert sha(k/n)==sha(k.parent/'video-resident-context222'/n)
r=dict(passed=True,initial_inventory_sha256=sha(k/'inventory.json'),
       final_sources={str(p.relative_to(k)):sha(p) for p in k.rglob('*') if p.is_file() and p.suffix in ['.c','.h','.py','.ps1']},
       table_relocation='Same16 offsets moved to one external constant in retirement.c, avoiding unused static header copies.',
       physical_access=False,guest_launch=False,gpu_writes=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('Final224 source/table pins PASS')
