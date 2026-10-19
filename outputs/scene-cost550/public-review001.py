"""Check public build sources and imports; no runtime claim for rebuilt bytes."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
P=Path('/home/paul/xbox-windows-native/scene-cost550-public001')
out=K/'public-build001.json';assert not out.exists()
r=read(P/'build.json');c=read(P/'scene-build/build.json');actual=read(K/'binary-review001.json')
assert r['exit_code']==c['exit_code']==0
assert r['source_sha256']==sha(W/'src/samples/graphics-ladder/scenebench.c')==read(K/'sample-build001.json')['source_sha256']
assert c['source_sha256']==sha(W/'src/samples/graphics-ladder/scenepresent.c')==read(K.parent/'d3d-window547/sample-build001.json')['source_sha256']
rows=[]
for name,index in [('scenebench.exe',1),('scene.exe',2)]:
 p=P/name;pe=pefile.PE(str(p));imports={(d.dll.decode().lower(),i.name.decode()) for d in pe.DIRECTORY_ENTRY_IMPORT for i in d.imports}
 expected={(i['dll'],i['name']) for i in actual['rows'][index]['imports']};assert imports==expected
 assert pe.FILE_HEADER.Machine==0x14c and (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
 rows.append(dict(name=name,sha256=sha(p),bytes=p.stat().st_size,imports=len(imports),imports_match_tested=True))
out.write_text(json.dumps(dict(passed=True,build_receipt_sha256=sha(P/'build.json'),scene_receipt_sha256=sha(P/'scene-build/build.json'),rows=rows,source_matches_tested=True,executable_runtime_qualified=False,scope='Public rebuild source/import equivalence; actual550 runtime applies to its separately pinned binaries'),indent=2)+'\n')
print('PASS public two-executable build, source/import equivalence')
