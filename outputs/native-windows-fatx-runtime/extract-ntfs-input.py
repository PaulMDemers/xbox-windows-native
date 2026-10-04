"""Extract the known private NTFS fixture for read-only file staging."""
from pathlib import Path
import subprocess,struct,shutil,json,hashlib,os
root=Path('/home/paul/xbox-windows-native');ws=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=root/'fixtures/fatx-fullboot-input';out.mkdir(exist_ok=True)
source=ws/'outputs/native-windows-nt5-kernel/artifacts/windows2000-integrated-001.qcow2';raw=out/'source.raw';part=out/'windows.ntfs'
assert not raw.exists() and not part.exists()
assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()=='640da2ccfe86774dd512d846d9674f19d7e642c0df008ca42952e97185e4445b'
subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
with raw.open('rb') as src,part.open('xb') as dst:
 m=src.read(512);assert m[450]==7;start,count=struct.unpack_from('<II',m,454);assert start==16777216;src.seek(start*512);left=count*512
 while left:
  b=src.read(min(left,4*1024**2));assert b;dst.write(b);left-=len(b)
assert raw.parent.resolve()==(root/'fixtures/fatx-fullboot-input').resolve();raw.unlink()
print(part)
