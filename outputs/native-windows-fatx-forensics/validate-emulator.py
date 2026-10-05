"""Cold-check snapshot contents against the same stopped disk and F write extents."""
import pathlib,sys,subprocess,json,hashlib,struct,re
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-fatx-forensics';run=ws/'work/runs/fatx-forensics-002'
assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures/forensics-validation.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
out=k/'artifacts/emulator-002';out.mkdir(exist_ok=True)
r={'scope':__doc__,'run':run.name,'snapshot_files':[]}
sha=lambda b:hashlib.sha256(b).hexdigest()
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 with raw.open('rb') as f:
  w=Writer(f,fatx.open_partition(f,raw,'E'));directory=1
  for name in ['apps','xwnfatro']:directory=struct.unpack_from('<I',w.directory(directory)['entries'][name][2],44)[0]
  names=list(w.directory(directory)['entries'])
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);part=fatx.open_partition(f,raw,'F')
  for name in names:
   if name=='default.xbe':continue
   assert name in ['snapshot.txt','fat-metadata.bin'] or re.fullmatch(r'cluster-[0-9a-f]{8}\.bin',name)
   data=w.read('apps/xwnfatro/'+name);(out/name).write_bytes(data)
   if name=='snapshot.txt':
    r['report']=data.decode('ascii');assert b'SNAPSHOT_COMPLETE success=1' in data
   elif name=='fat-metadata.bin':
    assert len(data)==4096+part.fat_size;f.seek(part.fat_offset-4096);assert f.read(len(data))==data
   else:
    cluster=int(name[8:16],16);assert len(data)==65536;f.seek(part.cluster_offset(cluster));assert f.read(65536)==data
   r['snapshot_files'].append({'name':name,'bytes':len(data),'sha256':sha(data)})
  r['xbe_sha256']=sha(w.read('apps/xwnfatro/default.xbe'))
  assert r['xbe_sha256']==sha((k/'artifacts/default.xbe').read_bytes())
 mapping=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(run/'hdd.qcow2')]))
 fstart=15633072*512;fend=fstart+472764096*512
 r['top_overlay_F_extents']=[v for v in mapping if v.get('depth')==0 and v['start']<fend and v['start']+v['length']>fstart and v.get('data')]
 assert not r['top_overlay_F_extents'],'Probe run allocated F: data extents'
 r['emulator_snapshot_passed']=True
finally:raw.unlink(missing_ok=True)
(k/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print({a:r[a] for a in ['xbe_sha256','emulator_snapshot_passed','top_overlay_F_extents']});print(r['report'])
