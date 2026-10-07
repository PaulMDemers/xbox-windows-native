"""Extract ERESOURCE/OWNER_ENTRY layouts from the exact owned NT5 kernel PDB."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
parser=k.parent/'native-windows-nt5-interrupts/read-pdb-layouts.py'
ns={'__file__':str(parser)};exec(parser.read_text().split('selected={}')[0],ns)
assert hashlib.sha256(ns['p']).hexdigest()=='29f5de2a8db7959875b8a615945bd6f16e50e5c5a9465dd8f71b37f37d671e9e'
r={n:{**ns['structs'][n],'fields':ns['fields'](ns['structs'][n]['field_list'])} for n in ['_ERESOURCE','_OWNER_ENTRY']}
r['pdb_sha256']=hashlib.sha256(ns['p']).hexdigest()
(k/'kernel-resource-layouts.json').write_text(json.dumps(r,indent=2)+'\n')
print('Matched kernel resource layouts extracted')
