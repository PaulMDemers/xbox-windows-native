"""Create an owned emulator fixture with only the diagnostic video miniport replaced."""
import pathlib,sys,subprocess,struct,json,hashlib
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
sys.path[:0]=[str(k.parent/'native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=k/'artifacts/physical-f-v2-001.qcow2';target=k/'artifacts/physical-video-001.qcow2';raw=root/'fixtures/physical-video-001.raw'
assert not raw.exists() and not target.exists()
r={'scope':__doc__}
with source.open('rb') as f:r['source_sha256']=hashlib.file_digest(f,'sha256').hexdigest()
assert r['source_sha256']==json.loads((k/'emulator-fixture-v2.json').read_text())['sha256']
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  path='winnt/system32/drivers/xboxvnt5.sys';data=(k/'artifacts/xboxvnt5-diagnostic.sys').read_bytes();at=1;parts=w.parts(path)
  r['original_miniport_sha256']=hashlib.sha256(w.read(path)).hexdigest()
  assert w.read(path)==(k/'package/F'/path).read_bytes()
  for name in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name][2],44)[0]
  c,off,e=w.directory(at)['entries'][parts[-1]];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(chain)==1 and len(data)<65536
  w.write_cluster(chain[0],data);b=bytearray(w.read_cluster(c));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(c,b);w.dirs={};assert w.read(path)==data;w.flush()
  r['miniport_sha256']=hashlib.sha256(data).hexdigest()
 subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(raw),str(target)],check=True)
 with target.open('rb') as f:r['sha256']=hashlib.file_digest(f,'sha256').hexdigest()
finally:raw.unlink(missing_ok=True)
(k/'emulator-fixture-video.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
