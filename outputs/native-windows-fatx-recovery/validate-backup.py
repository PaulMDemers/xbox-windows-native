"""Verify every captured metadata byte, independent directory coverage, and absence of F: writes."""
import pathlib,sys,subprocess,json,hashlib,struct
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-recovery';run=ws/'work/runs/fatx-recovery-backup-001'
assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/recovery-backup-validation.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
out=k/'artifacts/emulator-001';out.mkdir(exist_ok=True);r=dict(scope=__doc__,run=run.name)
sha=lambda b:hashlib.sha256(b).hexdigest()
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'E'))
  for name in ['snapshot.txt','fat-metadata.bin','cluster-data.bin']:(out/name).write_bytes(w.read('apps/xwnfatcheck/'+name))
  r['xbe_sha256']=sha(w.read('apps/xwnfatcheck/default.xbe'));assert r['xbe_sha256']==sha((k/'artifacts/default.xbe').read_bytes())
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  meta=(out/'fat-metadata.bin').read_bytes();f.seek(w.p.fat_offset-4096);assert f.read(len(meta))==meta
  blob=(out/'cluster-data.bin').read_bytes();expected=[1,2,3,4,128,1024]
  assert len(blob)==len(expected)*65540
  assert 'SNAPSHOT_COMPLETE success=1 requested_clusters=6' in (out/'snapshot.txt').read_text()
  for i,c in enumerate(expected):
   assert struct.unpack_from('<I',blob,i*65540)[0]==c
   f.seek(w.p.cluster_offset(c));assert f.read(65536)==blob[i*65540+4:(i+1)*65540]
  r.update(clusters_verified=len(expected),exact_bytes_verified=True)
 mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(run/'hdd.qcow2')]))
 lo=15633072*512;hi=lo+472764096*512
 r['top_overlay_F_extents']=[v for v in mapping if v.get('depth')==0 and v.get('data') and v['start']<hi and v['start']+v['length']>lo]
 assert not r['top_overlay_F_extents']
 r['emulator_snapshot_passed']=True
finally:raw.unlink(missing_ok=True)
(k/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)