"""Prepare matched physical-core/hive overlays; no guest/physical launch or mode/policy edits."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-windows-timing156'));import common as c
from allocation import scan
from restore import restore
sha=c.sha;read=c.read
base=ws/'outputs/video-physical-review159';capture=read(base/'capture.json');inputs=read(k.parent/'video-physical-rehearsal160/inputs.json');edit=read(base/'binding-edit.json')
assert capture['passed'] and inputs['passed'] and edit['only_two_expected_values_changed']
assert inputs['base_capture_sha256']==sha(base/'capture.json')
source=ws/'outputs/native-windows-fatx-forensics/artifacts/video-physical-rehearsal162-parent.qcow2';assert read(k/'parent-review.json')['virtual_contents_equal']
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(source)]))
parents=[dict(path=str(Path(v['filename']).resolve()),sha256=sha(Path(v['filename']))) for v in chain]
case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;out.mkdir(exist_ok=False)
target=ws/'outputs/native-windows-fatx-forensics/artifacts'/('video-physical-rehearsal162-'+case+'.qcow2');seed=ws/('work/video-physical-rehearsal162-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists()
probe=ws/'outputs/video-next/probe-v3/artifacts/gdi-probe.exe';runner=ws/'outputs/video-trace-reuse-settled/artifacts/runner.exe'
assert sha(probe)==read(ws/'outputs/video-next/probe-v3/build-review.json')['sha256']
payload=[('xwnrps01/replay.exe',probe.read_bytes()),('xwnrps01/runner.exe',runner.read_bytes())]
with c.ColdIO(source) as io:
    before=c.readers(io,source)
    for path in ['xwnrps01/replay.exe','xwnrps01/runner.exe','xwnrps01/attempt.log','xwnrps01/gdi-baseline.txt','xwnrps02/attempt.log']:
        try:before['F'].read(path)
        except KeyError:pass
        else:raise AssertionError('Old test/output path exists in selected parent: '+path)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
rows=[]
for root,items in [(base/'artifacts',capture['files']),(k.parent/'video-physical-rehearsal160/artifacts',inputs['files'])]:
    rows.extend((r,root/r['path'].lstrip('/')) for r in items)
candidate=read(ws/'outputs/video-hardware-candidate158/package-review.json');assert candidate['passed']
expected={};c.m.target=target;io=c.m.SliceIO(target)
for volume in ['F','E']:
    w=c.m.Writer(io,c.m.fatx.open_partition(io,target,volume))
    for row,p in rows:
        v,path=row['path'].lstrip('/').split('/',1)
        if v!=volume:continue
        if not row.get('present',True):
            try:w.read(path)
            except KeyError:continue
            else:raise AssertionError('Parent has component absent from physical snapshot: '+path)
        assert sha(p)==row['sha256'];data=p.read_bytes()
        if case=='candidate001' and path=='winnt/system32/config/system':
            data=(base/'artifacts/proposed-system').read_bytes();assert hashlib.sha256(data).hexdigest()==edit['after_sha256']
        restore(w,path,data);expected[volume+'/'+path]=hashlib.sha256(data).hexdigest()
    if case=='candidate001':
        for row in candidate['candidate']:
            v,path=row['target'].split('/',1)
            if v!=volume:continue
            p=ws/row['source'];assert sha(p)==row['sha256'];restore(w,path,p.read_bytes());expected[row['target']]=row['sha256']
    if volume=='F':
        for path,data in payload:w.write(path,data);expected['F/'+path]=hashlib.sha256(data).hexdigest()
        startup=b'@echo off\r\nC:\\xwnrps01\\runner.exe\r\nexit\r\n';restore(w,c.STARTUP,startup);expected['F/'+c.STARTUP]=hashlib.sha256(startup).hexdigest()
    w.flush()
with c.ColdIO(target) as io:
    rr=c.readers(io,target)
    for name,digest in expected.items():v,path=name.split('/',1);assert c.m.sha(rr[v].read(path))==digest
scan(target,out/'before/artifacts');allocation=read(out/'before/allocation.json');assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',source.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
for row in parents:assert sha(Path(row['path']))==row['sha256']
r=dict(case=case,prepared=True,launched=False,physical_writes=False,parents=parents,fixture_name=target.name,fixture_sha256=sha(target),seed_sha256=sha(seed),files=expected,
       base_capture_sha256=sha(base/'capture.json'),dependencies_sha256=sha(k.parent/'video-physical-rehearsal160/inputs.json'),binding_edit_sha256=sha(base/'binding-edit.json'),
       limits='Captured physical core/registry on an older licensed-media emulator disk; remaining files/partitions are not a whole-console clone. Physical unsupported-device policy/settings preserved. No emulator null-policy transplant. Generic GDI probe/launcher unchanged; old readback/timing coverage is limited. Fresh runtime/cold qualification required.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print('Fresh physical-core '+case+' readback/allocation passed; not launched')
