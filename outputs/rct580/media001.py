import hashlib,io,json,sys,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
exe=Path('C:/xwn580/runner-build001/run580.exe');b=json.loads((K/'runner-build001.json').read_text());assert b['status']=='compiled' and sha(exe)==b['rows'][0]['sha256']
p=Path('C:/xwn580/helper001.iso');assert not p.exists() and not (K/'media001.json').exists()
assert shutil.disk_usage('C:/').free-1024**2>=20*1024**3
batch=b'@echo off\r\nif exist C:\\xwn580-kit goto fail\r\nmkdir C:\\xwn580-kit\r\ncopy D:\\RUN580.EXE C:\\xwn580-kit\\RUN580.EXE\r\nif errorlevel 1 goto fail\r\nC:\\xwn580-kit\\RUN580.EXE /close=_BerksWin2kWelcomeApp_\r\nexit\r\n:fail\r\necho XWN580 COPY FAILED\r\npause\r\n'
iso=pycdlib.PyCdlib();iso.new(interchange_level=3,joliet=3,vol_ident='XWN580WELCOME')
iso.add_file(str(exe),iso_path='/RUN580.EXE;1',joliet_path='/RUN580.EXE');fp=io.BytesIO(batch);iso.add_fp(fp,len(batch),iso_path='/PREP.CMD;1',joliet_path='/PREP.CMD');iso.write(str(p));iso.close()
r=dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size,runner_sha256=sha(exe),copy_script=batch.decode(),physical_access=False)
(K/'media001.json').write_text(json.dumps(r,indent=2)+'\n')
check=pycdlib.PyCdlib();check.open(str(p));f=io.BytesIO();check.get_file_from_iso_fp(f,joliet_path='/RUN580.EXE');assert hashlib.sha256(f.getvalue()).hexdigest()==sha(exe)
f=io.BytesIO();check.get_file_from_iso_fp(f,joliet_path='/PREP.CMD');assert f.getvalue()==batch;check.close()
(K/'media-review001.json').write_text(json.dumps(dict(passed=True,media_sha256=sha(p),files=2,retail_assets=False),indent=2)+'\n')
print('Small media verified',p.stat().st_size)
