"""Original synthetic tracer CD only; no game/media copied to the fixture."""
import hashlib,io,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pycdlib
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=json.loads((K/'build001.json').read_text());assert b['status']=='compiled'
assert json.loads((K/'binary-review001.json').read_text())['passed']
out=K/'media001.json';p=Path('C:/xwn617/helper001.iso');assert not out.exists() and not p.exists()
assert shutil.disk_usage('C:/').free-16*1024**2>=20*1024**3
iso=pycdlib.PyCdlib();iso.new(interchange_level=3,joliet=3,vol_ident='XWN617TRACE');files={}
for row in b['rows']:
 path=Path(row['path'].replace('/mnt/c/','C:/'));assert sha(path)==row['sha256'];name=path.name.upper()
 iso.add_file(str(path),iso_path='/'+name+';1',joliet_path='/'+name);files[name]=row
lines=['@echo off','if exist C:\\xwn617-kit goto fail','mkdir C:\\xwn617-kit']
for name in files:lines+=['copy D:\\'+name+' C:\\xwn617-kit\\'+name,'if errorlevel 1 goto fail']
lines+=['attrib -R C:\\xwn617-kit\\*.*','echo XWN617 READY - EJECT CD BEFORE RUNNING','exit',':fail','echo COPY FAILED','pause']
data=('\r\n'.join(lines)+'\r\n').encode('ascii');fp=io.BytesIO(data)
iso.add_fp(fp,len(data),iso_path='/PREP.CMD;1',joliet_path='/PREP.CMD');iso.write(str(p));iso.close()
iso=pycdlib.PyCdlib();iso.open(str(p))
for name,row in files.items():
 f=io.BytesIO();iso.get_file_from_iso_fp(f,joliet_path='/'+name);assert hashlib.sha256(f.getvalue()).hexdigest()==row['sha256']
f=io.BytesIO();iso.get_file_from_iso_fp(f,joliet_path='/PREP.CMD');assert f.getvalue()==data
copies=[line for line in data.decode().splitlines() if line.startswith('copy ')]
assert copies==['copy D:\\'+n+' C:\\xwn617-kit\\'+n for n in files]
assert len(copies)==3 and data.decode().count('if errorlevel 1 goto fail')==3
iso.close()
out.write_text(json.dumps(dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,files=files,copy_script=data.decode(),readback_passed=True),indent=2)+'\n')
(K/'media-review001.json').write_text(json.dumps(dict(passed=True,media_sha256=sha(p),scope='Every compiled media member extracted and hash matched.'),indent=2)+'\n')
