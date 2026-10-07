"""Verify0101 format/checksum and unchanged imports against the reviewed0098 binary."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'work/python-packages'))
import pefile
data=(k/'artifacts/xwnfatx.sys').read_bytes();p=pefile.PE(data=data)
old=json.loads((k.parent/'fatx-paging-eof/binary-review.json').read_text())
imports={d.dll.decode():[i.name.decode() for i in d.imports] for d in p.DIRECTORY_ENTRY_IMPORT}
assert imports==old['imports']
assert p.FILE_HEADER.Machine==332 and p.OPTIONAL_HEADER.Subsystem==1
assert p.OPTIONAL_HEADER.CheckSum==p.generate_checksum()
report=json.loads((k/'build-report.json').read_text());manifest=json.loads((k/'manifest.json').read_text())
assert report['status']=='compiled' and report['verified_source_tree']==manifest['result_tree']
sha=hashlib.sha256(data).hexdigest();assert report['artifacts'][0]['sha256']==sha
r=dict(scope=__doc__,passed=True,sha256=sha,machine=p.FILE_HEADER.Machine,subsystem=p.OPTIONAL_HEADER.Subsystem,
       checksum=hex(p.OPTIONAL_HEADER.CheckSum),computed_checksum=hex(p.generate_checksum()),imports=imports,
       source_tree=manifest['result_tree'],parent_review_sha256=hashlib.sha256((k.parent/'fatx-paging-eof/binary-review.json').read_bytes()).hexdigest(),
       physical_qualified=False,runtime_qualified=False)
(k/'binary-review.json').write_text(json.dumps(r,indent=2)+'\n');print('Candidate format/checksum/import review passed: '+sha)
