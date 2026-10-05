"""Verify every captured metadata byte, independent directory coverage, and absence of F: writes."""
import pathlib,sys,subprocess,json,hashlib,struct
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-preflight';run=ws/'work/runs/fatx-preflight-001'
assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/preflight-validation.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
out=k/'artifacts/emulator-001';out.mkdir(exist_ok=True);r=dict(scope=__doc__,run=run.name)
sha=lambda b:hashlib.sha256(b).hexdigest()
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'E'))
  for name in ['snapshot.txt','fat-metadata.bin','directories.bin']:(out/name).write_bytes(w.read('apps/xwnfatcheck/'+name))
  r['xbe_sha256']=sha(w.read('apps/xwnfatcheck/default.xbe'));assert r['xbe_sha256']==sha((k/'artifacts/default.xbe').read_bytes())
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  meta=(out/'fat-metadata.bin').read_bytes();f.seek(w.p.fat_offset-4096);assert f.read(len(meta))==meta
  records=(out/'directories.bin').read_bytes();assert len(records)%80==0;captured=set();seen_clusters=set()
  for at in range(0,len(records),80):
   typ,head,c,aux=struct.unpack_from('<4I',records,at)
   if typ==1:assert w.fat[c]==aux;seen_clusters.add(c)
   elif typ==2:
    f.seek(w.p.cluster_offset(c)+aux);assert f.read(64)==records[at+16:at+80];captured.add((head,c,aux))
   elif typ==5:assert at+80==len(records)
   else:raise AssertionError(('Unexpected warning in known-good fixture',typ))
  expected=set();expected_clusters=set();queue=[1]
  for head in queue:
   if not head:continue
   assert head not in expected_clusters;expected_clusters.update(w.chain(head))
   for _,(c,off,e) in w.directory(head)['entries'].items():
    expected.add((head,c,off))
    if e[1]&16:queue.append(struct.unpack_from('<I',e,44)[0])
  assert expected==captured and expected_clusters==seen_clusters
  r.update(entries_verified=len(captured),directory_clusters_verified=len(seen_clusters),directory_coverage_exact=True)
 mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(run/'hdd.qcow2')]))
 lo=15633072*512;hi=lo+472764096*512
 r['top_overlay_F_extents']=[v for v in mapping if v.get('depth')==0 and v.get('data') and v['start']<hi and v['start']+v['length']>lo]
 assert not r['top_overlay_F_extents']
 r['emulator_snapshot_passed']=True
finally:raw.unlink(missing_ok=True)
(k/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
subprocess.run([sys.executable,str(k/'analyze.py'),'--capture',str(out),'--output',str(k/'emulator-allocation.json')],check=True)
assert json.loads((k/'emulator-allocation.json').read_text())['allocation_consistent']
