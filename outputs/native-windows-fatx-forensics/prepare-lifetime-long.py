"""Keep the qualified r14 disk, add repeat-boot verification and a fifteen-minute soak in a child overlay."""
import hashlib,json,pathlib,shutil,struct,subprocess,sys,tempfile
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-forensics'
run='nt5-physical-f-high-allocation-r14';source=ws/'work/runs'/run/'hdd.qcow2';checkpoint=k/'artifacts/lifetime-checkpoint-001.qcow2'
parent=k/'artifacts/lifetime-retired-001.qcow2';target=k/'artifacts/lifetime-long-001.qcow2';seed=ws/'work/lifetime-long-seed.qcow2'
assert (source.parent/'cleanup.json').exists() and json.loads((k/(run+'-qualification.json')).read_text())['passed']
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/lifetime-long.raw')
assert not any(p.exists() for p in [checkpoint,target,seed,raw])
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(source);assert sha(parent)==json.loads((k/'lifetime-retired-fixture.json').read_text())['fixture_sha256']
assert pathlib.Path(json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]))['full-backing-filename']).resolve()==parent.resolve()
shutil.copyfile(source,checkpoint);subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(checkpoint)],check=True)
checkpoint_sha=sha(checkpoint)
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
patches=[]
class Tracking:
 def __init__(self,f):self.f=f
 def __getattr__(self,name):return getattr(self.f,name)
 def write(self,b):patches.append((self.f.tell(),bytes(b)));return self.f.write(b)
def replace(w,path,data):
 parent=1;parts=w.parts(path)
 for part in parts[:-1]:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part.lower()][2],44)[0]
 dc,off,e=w.directory(parent)['entries'][parts[-1].lower()];chain=list(w.chain(struct.unpack_from('<I',e,44)[0]))
 assert len(data)<=len(chain)*w.p.cluster_size
 for i,c in enumerate(chain):w.write_cluster(c,data[i*w.p.cluster_size:(i+1)*w.p.cluster_size])
 b=bytearray(w.read_cluster(dc));struct.pack_into('<I',b,off+48,len(data));w.write_cluster(dc,b);w.dirs={};assert w.read(path)==data
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(checkpoint),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(Tracking(f),fatx.open_partition(f,raw,'F'))
  trace=w.read('winnt/system32/xwn-video-trace.bin');assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
  (k/'artifacts/r14-video-trace.bin').write_bytes(trace);replace(w,'winnt/system32/xwn-video-trace.bin',trace[:16]+bytes(4080))
  helper=(k/'artifacts/xwnlongsoak.exe').read_bytes();verify=(k/'artifacts/xwnlifeverify.exe').read_bytes()
  replace(w,'xwnphys2.exe',helper);w.write('xwnlifeverify.exe',verify)
  startup=b'@echo off\r\nC:\\xwnrename.exe\r\nif errorlevel 1 exit\r\nC:\\xwnrotate.exe\r\nif errorlevel 1 exit\r\nC:\\xwnlifeverify.exe\r\nif errorlevel 1 exit\r\nC:\\xwnphys2.exe\r\n'
  replace(w,'Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',startup);w.flush()
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(checkpoint),str(target)],check=True)
 with tempfile.TemporaryDirectory() as temp:
  args=[]
  for i,(off,data) in enumerate(patches):
   p=pathlib.Path(temp)/str(i);p.write_bytes(data);args+=['-c',f'write -q -s {p} {off} {len(data)}']
  subprocess.run(['qemu-io','-f','qcow2',*args,str(target)],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',checkpoint.name,str(target)],check=True)
 raw.unlink();subprocess.run(['qemu-img','convert','-O','raw',str(target),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'F'));assert w.read('xwnphys2.exe')==helper and w.read('xwnlifeverify.exe')==verify
  assert w.read('xwnrotate/state.bin')==struct.pack('<I',1) and w.read('winnt/system32/xwn-video-trace.bin')==trace[:16]+bytes(4080)
 assert sha(source)==before and sha(checkpoint)==checkpoint_sha
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
 r=dict(scope=__doc__,source_run=run,source_sha256=before,checkpoint_sha256=checkpoint_sha,fixture_sha256=sha(target),long_soak_sha256=hashlib.sha256(helper).hexdigest(),reboot_verifier_sha256=hashlib.sha256(verify).hexdigest(),original_trace_sha256=hashlib.sha256(trace).hexdigest(),readback_verified=True)
 (k/'lifetime-long-fixture.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
