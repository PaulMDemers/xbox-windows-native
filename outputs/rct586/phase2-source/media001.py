"""Independent NT5/import/frozen-source review, then a tiny phase-2 transfer CD."""
from pathlib import Path
import hashlib,json,io,sys
K=Path(__file__).resolve().parent;T=K.parent;W=T.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile,pycdlib
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
b=json.loads((K/'build002.json').read_text());assert b['status']=='compiled'
for name,row in b['files'].items():
    p=Path(name.replace('/mnt/c/','C:/'));assert sha(p)==row['sha256']
    if p.suffix in ('.c','.h'):assert p.read_bytes()==(K/p.name).read_bytes()
exe=Path('C:/xwn586/phase2-build001/load586.exe');pe=pefile.PE(str(exe))
assert pe.FILE_HEADER.Machine==0x14c and pe.OPTIONAL_HEADER.MajorSubsystemVersion==5 and pe.OPTIONAL_HEADER.MinorSubsystemVersion==0
imports={d.dll.decode():[i.name.decode() for i in d.imports] for d in pe.DIRECTORY_ENTRY_IMPORT}
known=json.loads((T/'binary-review001.json').read_text())['files'][0]['imports']
assert all(d in known and set(names)<=set(known[d]) for d,names in imports.items())
iso=Path('C:/xwn586/phase2-helper001.iso');assert not iso.exists()
cd=pycdlib.PyCdlib();cd.new(interchange_level=3,joliet=3,vol_ident='XWN586LOAD')
cd.add_file(str(exe),iso_path='/LOAD586.EXE;1',joliet_path='/LOAD586.EXE')
cmd=b'@echo off\r\nif exist C:\\xwn586-kit\\load586.exe goto fail\r\ncopy D:\\LOAD586.EXE C:\\xwn586-kit\\load586.exe\r\nif errorlevel 1 goto fail\r\nexit\r\n:fail\r\necho PHASE2 COPY FAILED\r\npause\r\n'
cd.add_fp(io.BytesIO(cmd),len(cmd),iso_path='/PREP586.CMD;1',joliet_path='/PREP586.CMD');cd.write(str(iso));cd.close()
cd=pycdlib.PyCdlib();cd.open(str(iso));f=io.BytesIO();cd.get_file_from_iso_fp(f,joliet_path='/LOAD586.EXE');assert f.getvalue()==exe.read_bytes();cd.close()
out=K/'media001.json';assert not out.exists();r={'passed':True,'path':str(iso),'sha256':sha(iso),'exe_sha256':sha(exe),'imports':imports,'manual_observation_seconds':360,'automatic_load_success_claim':False,'frozen_source_verified':True};out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':True,'bytes':iso.stat().st_size}))
