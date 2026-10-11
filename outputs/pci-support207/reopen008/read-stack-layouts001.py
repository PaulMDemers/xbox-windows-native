"""Extract ownership structures from the pinned shared, read-only NT5 PDB."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[2]
parser=repo/'outputs/native-windows-nt5-interrupts/read-pdb-layouts.py'
root=Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
# The private PCI checkout has no PDB. Resolve the existing shared symbol input;
# the parser prefix only reads it and builds dictionaries, without file writes.
ns={'__file__':str(root/'outputs/native-windows-nt5-interrupts/read-pdb-layouts.py')}
exec(parser.read_text().split('selected={}')[0],ns)
digest=hashlib.sha256(ns['p']).hexdigest()
assert digest=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
names=['_KTHREAD','_ETHREAD']
r=dict(pdb_sha256=digest,parser_sha256=hashlib.sha256(parser.read_bytes()).hexdigest(),pdb_path=str(root/'work/symbols/ntoskrnl-2195-7376.pdb'),structures={n:{**ns['structs'][n],'fields':ns['fields'](ns['structs'][n]['field_list'])} for n in names})
dest=k/'stack-layouts001.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r['structures'][n] for n in names if n not in ('_EPROCESS','_FILE_OBJECT')},indent=2))
