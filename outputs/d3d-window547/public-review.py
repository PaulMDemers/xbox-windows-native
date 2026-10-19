"""MIT. Public builder provenance; source agreement is not binary identity."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=Path('/home/paul/xbox-windows-native/d3d-window547-public001');r=json.loads((P/'build.json').read_text());s=json.loads((K/'sample-build001.json').read_text())
assert r['exit_code']==0 and r['source_sha256']==s['source_sha256']==sha(W/'src/samples/graphics-ladder/scenepresent.c')
p=P/'scenepresent.exe';assert sha(p)==r['executable_sha256'];pe=pefile.PE(str(p));assert pe.OPTIONAL_HEADER.MajorSubsystemVersion==5 and pe.OPTIONAL_HEADER.MinorSubsystemVersion==0
b=json.loads((K/'binary-review001.json').read_text());tested={(x['dll'],x['name']) for x in b['rows'][1]['imports']};actual={(e.dll.decode().lower(),i.name.decode()) for e in pe.DIRECTORY_ENTRY_IMPORT for i in e.imports};assert actual==tested
(K/'public-build001.json').write_text(json.dumps(dict(passed=True,build=r,tested_source_sha256=s['source_sha256'],import_count=len(actual),runtime_binary_sha256=s['executable_sha256'],public_binary_sha256=sha(p),byte_identical=sha(p)==s['executable_sha256'],scope='Public command compiles exact tested source; static NT5 import equality. Public executable not separately run.'),indent=2)+'\n')
print('Public source/import review passed')
