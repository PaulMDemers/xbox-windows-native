"""Close the failed first control and freeze its exact source/checker closure."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'tools'));import graphics_present as g
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final-review.json';capsule=Path('/home/paul/xbox-windows-native/presentation439-inputs001')
assert not out.exists() and not capsule.exists()
state=json.loads((K/'ntfs-phase1.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text())
ind=json.loads((K/'independent001.json').read_text());review=json.loads((K/'runtime-review001.json').read_text())
assert state['closed'] and state['exit_code']==0 and not state['deadline'] and not review['all_allowed_cases_passed']
assert ind['passed'] and ind['closed'] and ind['mount_absent'] and ind['disk_unchanged'] and cold['normal_shutdown_delta']==1
root=Path(cold['private_path'])/'files/xwn439';rows=[]
for name in ('r03d','r03s'):
 total=0
 for kind in ('source','before','after'):
  actual=(root/(name+'-'+kind+'.bin')).read_bytes();assert actual==g.expected(0,kind);total+=len(actual)
 rows.append(dict(name=name,stage0_exact_bytes=total,full_case_passed=False,stopped_at='s1.clip.exact=0 before covered capture/blit'))
capsule.mkdir();pins=dict(review['frozen_dependencies'])
for p in (W/'src/samples/graphics-ladder/present.c',W/'src/samples/graphics-ladder/present.cmd',W/'tools/build-graphics-samples.py',W/'tests/test_graphics_present.py'):pins[str(p)]=sha(p)
archived={}
for i,(path,h) in enumerate(sorted(pins.items())):
 p=Path(path);assert sha(p)==h,path;dest=capsule/f'{i:03d}-{p.name}';dest.write_bytes(p.read_bytes());assert sha(dest)==h
 archived[path]=dict(path=str(dest),sha256=h)
for name in ('build001.json','sample-build001.json'):
 b=json.loads((K/name).read_text())
 for p,h in b['headers'].items():assert sha(Path(p))==h
for row in json.loads((K/'build001.json').read_text())['rows']:assert sha(Path(row['path']))==row['sha256']
prep=json.loads((K/'ntfs-preparation001.json').read_text());P=Path(prep['path'])
assert sha(Path(prep['source']))==prep['source_sha256'] and sha(P/'probe.img')==prep['floppy_sha256'] and sha(P/'disk.qcow2')==state['disk_sha256']
assert not list(P.glob('phase*/qmp.sock'))
private={str(p):sha(p) for folder in (P,Path(ind['private_path']),capsule) for p in folder.rglob('*') if p.is_file()}
record=dict(full_rung03_passed=False,partial=rows,normal_restart=True,owned_guest_closed=True,independent_files=len(ind['rows']),private_files=private,frozen_inputs=archived,
 known_limitations=['Stage1 clip region did not exclude cover; original test did not independently establish cover Z-order','No full NTFS allocation audit','Inherited SOFTWARE unknown typed DRM value','No Xbox run, scanout or GPU qualification'])
out.write_text(json.dumps(record,indent=2)+'\n');print('Failed control preserved, exact initial pixels independently verified, input closure archived:',len(archived))
