"""Read back every helper file and mapped retail member against source manifest."""
import hashlib,io,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pycdlib
m=json.loads((K/'media001.json').read_text());a=json.loads((K/'asset-integrity001.json').read_text());mapping=json.loads((K.parent/'rct577/disc-mapping001.json').read_text())
h=hashlib.file_digest(open(m['path'],'rb'),'sha256').hexdigest();assert h==m['sha256']
i=pycdlib.PyCdlib();i.open(m['path'])
for name,v in m['files'].items():
 f=io.BytesIO();i.get_file_from_iso_fp(f,joliet_path='/'+name);data=f.getvalue();assert len(data)==v['bytes'] and hashlib.sha256(data).hexdigest()==v['sha256']
 if name.startswith('game/'):assert hashlib.sha1(data).hexdigest()==a[name]['sha1']
f=io.BytesIO();i.get_file_from_iso_fp(f,joliet_path='/PREP.CMD');assert f.getvalue()==m['copy_script'].encode('ascii');i.close()
assert set(mapping['mapped_files'])|set(mapping['supplemental_files'])|{'game/Saved Games/XWN593.SV4'}==set(a)
assert not set(mapping['mapped_files'])&set(mapping['supplemental_files'])
i=pycdlib.PyCdlib();i.open(mapping['source_iso']['path'])
for name,v in mapping['mapped_files'].items():
 f=io.BytesIO();i.get_file_from_iso_fp(f,joliet_path=v['source']);data=f.getvalue();assert len(data)==a[name]['bytes'] and hashlib.sha256(data).hexdigest()==a[name]['sha256'] and hashlib.sha1(data).hexdigest()==a[name]['sha1']
i.close()
from copy_contract import validate
contract=validate(m['copy_script'],m['files'],json.loads((K/'build001.json').read_text())['rows'],618)
(K/'media-review001.json').write_text(json.dumps(dict(passed=True,media_sha256=h,helper_files=len(m['files']),mapped_files=len(mapping['mapped_files']),all_assets=len(a),copy_contract=contract,guest_copy_qualified=False,physical_access=False),indent=2)+'\n')
print('Independent readback passed',len(a))
