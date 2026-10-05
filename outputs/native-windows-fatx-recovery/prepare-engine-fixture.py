"""Stage the native repair engine in an owned low-LBA fixture with exact before/after sectors."""
import argparse,hashlib,json,pathlib,struct,subprocess,sys,tempfile,os
p=argparse.ArgumentParser();p.add_argument('--case',choices=['apply','reject','resume'],required=True);a=p.parse_args()
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-recovery'
src=k/'artifacts/backup-fixture-001.qcow2';target=k/f'artifacts/repair-{a.case}-001.qcow2';raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/f'repair-{a.case}.raw'
assert not raw.exists() and not target.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
ranges=[]
class Tracking:
 def __init__(self,f):self.f=f
 def __getattr__(self,n):return getattr(self.f,n)
 def write(self,b):ranges.append((self.f.tell(),self.f.tell()+len(b)));return self.f.write(b)
sha=lambda b:hashlib.sha256(b).hexdigest()
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(raw)],check=True)
 with raw.open('r+b') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'));f.seek(w.p.fat_offset-4096);meta=f.read(14778368)
  root=w.read_cluster(1);sector_offsets=sorted({off//512*512 for c,off,e in w.directory(1)['entries'].values() if c==1});assert len(sector_offsets)>=2
  records=[]
  for off in sector_offsets[:2]:
   first=next(at for at in range(off,off+512,64) if 1<=root[at]<=42)
   before=root[off:off+512];after=bytearray(before);after[first-off+56]^=1
   records.append((len(meta)+off,before,bytes(after)))
  plan_records=list(records)
  if a.case=='reject':
   off,before,after=plan_records[1];bad=bytearray(before);bad[127]^=0x80;plan_records[1]=(off,bytes(bad),after)
  if a.case=='resume':
   off,before,after=records[0];f.seek(15633072*512+off);f.write(after);ranges.append((15633072*512+off,15633072*512+off+512))
  plan=struct.pack('<16sI',b'XWN-FIX-0001',2)+b''.join(struct.pack('<Q',off)+before+after for off,before,after in plan_records)
  writer=Writer(Tracking(f),fatx.open_partition(f,raw,'E'))
  for name,data in [('default.xbe',(k/'artifacts/repair.xbe').read_bytes()),('plan.bin',plan),('fat-before.bin',meta)]:writer.write('Apps/XWNFatFix/'+name,data)
  writer.flush();merged=[]
  for lo,hi in sorted(ranges):
   if merged and lo<=merged[-1][1]:merged[-1][1]=max(hi,merged[-1][1])
   else:merged.append([lo,hi])
  subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(src),str(target)],check=True)
  with tempfile.TemporaryDirectory() as temp:
   args=[]
   for i,(lo,hi) in enumerate(merged):
    f.seek(lo);part=pathlib.Path(temp)/str(i);part.write_bytes(f.read(hi-lo));args+=['-c',f'write -q -s {part} {lo} {hi-lo}']
   subprocess.run(['qemu-io','-f','qcow2',*args,str(target)],check=True,stdout=subprocess.DEVNULL)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',src.name,str(target)],check=True)
 result=dict(case=a.case,xbe_sha256=sha((k/'artifacts/repair.xbe').read_bytes()),plan_sha256=sha(plan),metadata_sha256=sha(meta),records=[dict(offset=off,before_hex=before.hex(),after_hex=after.hex()) for off,before,after in records])
 (k/f'repair-{a.case}-fixture.json').write_text(json.dumps(result,indent=2)+'\n')
 seed=ws/f'work/repair-{a.case}-seed.qcow2';assert not seed.exists()
 subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
 subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-recovery/artifacts/'+target.name,str(seed)],check=True)
finally:raw.unlink(missing_ok=True)
