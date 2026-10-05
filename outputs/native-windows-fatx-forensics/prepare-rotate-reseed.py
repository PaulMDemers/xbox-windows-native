"""Preserve the one-shot video trace, then reset only its existing 4096 bytes for boot two."""
import hashlib,json,pathlib,struct,subprocess,sys,tempfile
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
source=k/'artifacts/rotate-checkpoint-001.qcow2';target=k/'artifacts/rotate-reboot-002.qcow2';seed=ws/'work/rotate-reboot2-seed.qcow2'
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/rotate-reseed.raw')
assert not target.exists() and not raw.exists() and not seed.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(source);assert before==json.loads((k/'rotate-reboot-fixture.json').read_text())['checkpoint_sha256']
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  path='winnt/system32/xwn-video-trace.bin';trace=w.read(path)
  assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
  count=struct.unpack_from('<I',trace,16)[0];assert 0<count<=254
  saved=k/'artifacts/r9-video-trace.bin';assert not saved.exists();saved.write_bytes(trace)
  parent=1
  for part in ['winnt','system32']:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part][2],44)[0]
  entry=w.directory(parent)['entries']['xwn-video-trace.bin'][2]
  chain=list(w.chain(struct.unpack_from('<I',entry,44)[0]));assert len(chain)==1
  # Locate the cluster through the existing writer's read routine, avoiding guessed geometry.
  w.read_cluster(chain[0]);offset=f.tell()-w.p.cluster_size
 data=trace[:16]+bytes(4080)
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
 with tempfile.NamedTemporaryFile() as patch:
  patch.write(data);patch.flush()
  subprocess.run(['qemu-io','-f','qcow2','-c',f'write -q -s {patch.name} {offset} 4096',str(target)],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
 raw.unlink();subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'F'));assert w.read(path)==data;assert w.read('xwnrotate/state.bin')==struct.pack('<I',1)
 assert sha(source)==before
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
 r=dict(scope=__doc__,source_sha256=before,fixture_sha256=sha(target),trace_before_sha256=hashlib.sha256(trace).hexdigest(),trace_records=count,seed_sha256=hashlib.sha256(data).hexdigest(),changed_guest_offset=offset,changed_guest_bytes=4096,readback_verified=True)
 (k/'rotate-reseed-fixture.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
