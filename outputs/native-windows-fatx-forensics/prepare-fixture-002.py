"""Stage only owned E: app writes into a small overlay; preserve the F: source."""
import sys,pathlib,subprocess,json,hashlib,tempfile,os
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=root/'outputs/native-windows-fatx-forensics'
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/fatx-forensics.raw')
src=root/'outputs/native-windows-physical-f/artifacts/physical-cache-soak-001.qcow2'
target=k/'artifacts/snapshot-fixture-002.qcow2'
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts');import fatx_stage_boot as fatx
assert not raw.exists() and not target.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r={'scope':__doc__,'source_sha256':sha(src)};ranges=[]
class Tracking:
 def __init__(self,fp):self.fp=fp
 def __getattr__(self,name):return getattr(self.fp,name)
 def write(self,data):
  at=self.fp.tell();ranges.append((at,at+len(data)));return self.fp.write(data)
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(raw)],check=True)
 with raw.open('r+b') as base:
  fp=Tracking(base);part=fatx.open_partition(fp,raw,'E')
  data=(k/'artifacts/default.xbe').read_bytes()
  r['file']=fatx.write_path_file(fp,part,'Apps/XWNFatRO/default.xbe',data).__dict__
  assert fatx.read_path_file(fp,part,'Apps/XWNFatRO/default.xbe')==data
  start,size=fatx.PARTITIONS['E'];assert all(start<=a<b<=start+size for a,b in ranges)
  merged=[]
  for a,b in sorted(ranges):
   if merged and a<=merged[-1][1]:merged[-1][1]=max(b,merged[-1][1])
   else:merged.append([a,b])
  subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(src),str(target)],check=True)
  with tempfile.TemporaryDirectory(prefix='xwn-fat-ro-') as tmp:
   commands=[]
   for i,(a,b) in enumerate(merged):
    base.seek(a);p=pathlib.Path(tmp)/str(i);p.write_bytes(base.read(b-a));commands+=['-c',f'write -q -s {p} {a} {b-a}']
   subprocess.run(['qemu-io','-f','qcow2',*commands,str(target)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',os.path.relpath(src,target.parent),str(target)],check=True)
 assert sha(src)==r['source_sha256']
 r.update(sha256=sha(target),source_preserved=True,changed_ranges=merged,changed_bytes=sum(b-a for a,b in merged))
 (k/'fixture-002.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
finally:raw.unlink(missing_ok=True)
