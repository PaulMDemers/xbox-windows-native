"""Use native WSL paths to compare compiled PE sections; no execution."""
from pathlib import Path
import json,hashlib,sys
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'work/python-packages'));import pefile
P=Path('/home/paul/xbox-windows-native/d3d-scene496-public-build001')
out=K/'public-build-review001.json';assert not out.exists()
r=json.loads((P/'build.json').read_text());assert r['exit_code']==0
(K/'public-build001.json').write_bytes((P/'build.json').read_bytes())
a=Path('/home/paul/xbox-windows-native/d3d-scene496-runner-build001/d3d.exe');b=P/'scene.exe'
x,y=pefile.PE(str(a)),pefile.PE(str(b));rows=[]
for l,z in zip(x.sections,y.sections):
 assert l.Name==z.Name and l.VirtualAddress==z.VirtualAddress and l.get_data()==z.get_data(),l.Name
 rows.append(dict(name=l.Name.rstrip(b'\0').decode(),rva=l.VirtualAddress,sha256=hashlib.sha256(l.get_data()).hexdigest()))
assert len(x.sections)==len(y.sections)
out.write_text(json.dumps(dict(passed=True,sections_byte_identical=rows,whole_binaries_identical=a.read_bytes()==b.read_bytes(),public_sha256=hashlib.sha256(b.read_bytes()).hexdigest(),control_sha256=hashlib.sha256(a.read_bytes()).hexdigest(),public_os_version=[y.OPTIONAL_HEADER.MajorOperatingSystemVersion,y.OPTIONAL_HEADER.MinorOperatingSystemVersion],control_os_version=[x.OPTIONAL_HEADER.MajorOperatingSystemVersion,x.OPTIONAL_HEADER.MinorOperatingSystemVersion],scope='Public builder compiled. All PE section bytes match private control binary; headers/timestamp differ. No separate execution of public build.'),indent=2)+'\n');print('Public builder sections match:',len(rows))
