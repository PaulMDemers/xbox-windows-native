"""Owned emulator overlay with cycle011's five registry hives, not a disk clone."""
import pathlib,sys,subprocess,struct,json,hashlib,tempfile
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
sys.path[:0]=[str(k.parent/'native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=k/'artifacts/physical-cache-stress-candidate-001.qcow2';target=k/'artifacts/physical-hives-011.qcow2';raw=root/'fixtures/physical-hives-011.raw'
assert not raw.exists() and not target.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
with source.open('rb') as f:source_sha=hashlib.file_digest(f,'sha256').hexdigest()
assert source_sha==json.loads((k/'emulator-fixture-cache-stress-candidate.json').read_text())['sha256']
audit=json.loads((k/'physical-011-binary-audit.json').read_text());assert audit['complete'] and audit['passed']
hive_audit=json.loads((k/'physical-011-hive-audit.json').read_text())
assert all(v['sequence1']==v['sequence2'] and v['checksum_valid'] and v['tree']['passed'] for v in hive_audit)
changes=[];patches={}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'));fat_before=w.fat[:]
  def write_cluster(c,b):
   b=bytes(b).ljust(w.p.cluster_size,b'\0');assert len(b)==w.p.cluster_size
   offset=w.p.cluster_offset(c);patches[offset]=b;f.seek(offset);f.write(b)
  w.write_cluster=write_cluster
  for v in audit['hives']:
   path='winnt/system32/config/'+v['name'];data=(k/'artifacts'/('physical-011-'+v['name'])).read_bytes();assert sha(data)==v['sha256']
   old=w.read(path);at=1;parts=w.parts(path)
   for name in parts[:-1]:at=struct.unpack_from('<I',w.directory(at)['entries'][name][2],44)[0]
   c,off,e=w.directory(at)['entries'][parts[-1]];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]));need=(len(data)+w.p.cluster_size-1)//w.p.cluster_size
   if need>len(chain):
    extra=w.allocate(need-len(chain));w.fat[chain[-1]]=extra[0];chain+=extra
   # Retain pre-existing capacity if the replacement is smaller.
   for i,cluster in enumerate(chain):w.write_cluster(cluster,data[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
   b=bytearray(w.read_cluster(c));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(c,b);w.dirs.clear()
   assert w.read(path)==data
   changes.append({'path':path,'old_sha256':sha(old),'new_sha256':sha(data),'bytes':len(data)})
  if w.fat!=fat_before:
   w.flush();f.seek(w.p.fat_offset);patches[w.p.fat_offset]=f.read(w.p.fat_size)
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
 with tempfile.TemporaryDirectory(prefix='xwn-hive-delta-') as tmp:
  commands=[]
  for i,(offset,b) in enumerate(patches.items()):
   p=pathlib.Path(tmp)/str(i);p.write_bytes(b);commands+=['-c',f'write -q -s {p} {offset} {len(b)}']
  subprocess.run(['qemu-io','-f','qcow2',*commands,str(target)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
 subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'F'))
  for v in changes:assert sha(w.read(v['path']))==v['new_sha256']
 with target.open('rb') as f:target_sha=hashlib.file_digest(f,'sha256').hexdigest()
 r={'scope':__doc__,'source_sha256':source_sha,'backing':source.name,'sha256':target_sha,'changes':changes,'limitation':'Other files, user hives, allocation layout and devices remain emulator fixtures.'}
 (k/'emulator-fixture-physical-hives-011.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
