"""Paging-write tail candidate overlay on the captured physical registry."""
import pathlib,sys,subprocess,struct,json,hashlib,tempfile
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
sys.path[:0]=[str(k.parent/'native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=k/'artifacts/physical-hives-011.qcow2';target=k/'artifacts/physical-cache-write-tail-001.qcow2';raw=root/'fixtures/physical-cache-write-tail-001.raw'
assert not raw.exists() and not target.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
with source.open('rb') as f:source_sha=hashlib.file_digest(f,'sha256').hexdigest()
assert source_sha==json.loads((k/'emulator-fixture-physical-hives-011.json').read_text())['sha256']
startup=b'@echo off\r\nC:\\xwnphys2.exe\r\n'
changes=[('winnt/system32/drivers/xwnfatx.sys',(k/'artifacts/xwnfatx-deferred.sys').read_bytes(),(k/'artifacts/xwnfatx-write-tail.sys').read_bytes())]
patches=[]
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  for path,old,data in changes:
   assert w.read(path)==old
   at=1;parts=w.parts(path)
   for name in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name][2],44)[0]
   c,off,e=w.directory(at)['entries'][parts[-1]];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));assert len(chain)*w.p.cluster_size>=len(data)
   for i,cluster in enumerate(chain):patches.append((w.p.cluster_offset(cluster),data[i*w.p.cluster_size:(i+1)*w.p.cluster_size].ljust(w.p.cluster_size,b'\0')))
   b=bytearray(w.read_cluster(c));struct.pack_into('<I',b,off+48,len(data));patches.append((w.p.cluster_offset(c),b))
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
 with tempfile.TemporaryDirectory(prefix='xwn-desktop-delta-') as tmp:
  commands=[]
  for i,(offset,b) in enumerate(patches):
   p=pathlib.Path(tmp)/str(i);p.write_bytes(b);commands+=['-c',f'write -q -s {p} {offset} {len(b)}']
  subprocess.run(['qemu-io','-f','qcow2',*commands,str(target)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
 subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'F'))
  for path,old,data in changes:assert w.read(path)==data
 with target.open('rb') as f:target_sha=hashlib.file_digest(f,'sha256').hexdigest()
 r={'scope':__doc__,'source_sha256':source_sha,'backing':source.name,'sha256':target_sha,'changes':[{'path':'F/'+p,'old_sha256':sha(o),'new_sha256':sha(n)} for p,o,n in changes]}
 (k/'emulator-fixture-physical-cache-write-tail-001.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
