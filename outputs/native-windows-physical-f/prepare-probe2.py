"""Create a fresh private native F fixture for the explicit-error probe."""
import pathlib,sys,subprocess,struct,json,hashlib
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
sys.path[:0]=[str(k.parent/'native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=k/'artifacts/physical-f-003.qcow2';target=k/'artifacts/physical-f-v2-001.qcow2';raw=root/'fixtures/physical-f-v2-001.raw'
assert not raw.exists() and not target.exists()
r={'scope':'Private emulator probe v2 fixture','files':[]}
with source.open('rb') as f:r['source_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
assert r['source_sha256']==json.loads((k/'emulator-fixture-003.json').read_text())['sha256']
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  for path,data in [('xwnphys2.exe',(k/'artifacts/xwnphys2.exe').read_bytes()),('xwn-report-v2.txt',b'XWN-V2-PENDING-20261004\r\n'.ljust(4096,b' '))]:
   w.write(path,data);assert w.read(path)==data;r['files'].append({'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
  path='documents and settings/all users/start menu/programs/startup/xwnsetup.cmd';data=b'@echo off\r\nC:\\xwnphys2.exe\r\n';at=1;parts=w.parts(path)
  for name in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name][2],44)[0]
  c,off,e=w.directory(at)['entries'][parts[-1]];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(chain)==1
  w.write_cluster(chain[0],data);b=bytearray(w.read_cluster(c));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(c,b);w.dirs={};assert w.read(path)==data
  # Match the physical dashboard-compatible archival name for this text log.
  at=struct.unpack_from('<I',w.directory(1)['entries']['winnt'][2],44)[0];c,off,e=w.directory(at)['entries']['com+.log'];b=bytearray(w.read_cluster(c));name=b'com-plus.log';b[off]=len(name);b[off+2:off+44]=name.ljust(42,b'\xff');w.write_cluster(c,b);w.dirs={}
  assert w.read('winnt/com-plus.log')==(k/'package/F/winnt/com+.log').read_bytes()
  w.flush()
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 with target.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
finally:raw.unlink(missing_ok=True)
(k/'emulator-fixture-v2.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
