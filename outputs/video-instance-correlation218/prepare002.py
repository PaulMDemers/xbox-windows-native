"""NEW disposable stock-kernel fixture: explicit app at both owned boot entries."""
import json,sys,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/video-gpu-handoff216'))
from common import ColdIO,readers,scan,sha,read,m
sys.path.insert(0,str(ws/'outputs/setup-wizard-automation201'));from restore import restore
root=Path('/mnt/e/Codex-archive/xbox-windows-native/instance218');root.mkdir(exist_ok=True)
source=Path('/mnt/e/Codex-archive/xbox-windows-native/gstate216/control001-source.qcow2')
original=read(ws/'outputs/video-instance-backing217/inputs.json')['parent_sha256'];assert sha(source)==original
target=root/'correlation002-preparation.qcow2';final=root/'correlation002-source.qcow2'
out=k/'prepare002';assert not out.exists() and not target.exists() and not final.exists();out.mkdir();art=out/'artifacts';art.mkdir()
review=read(k/'build-review.json');assert review['passed']
binary=k/'artifacts/build002/default.xbe'
expected=next(v for p,v in review['files'].items() if p.endswith('build002\\default.xbe') or p.endswith('build002/default.xbe'));assert sha(binary)==expected
m.fatx.PARTITIONS['C']=(0x465400*512,0xfa000*512)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(source),str(target)],check=True)
m.target=target;io=m.SliceIO(target);c=m.Writer(io,m.fatx.open_partition(io,target,'C'))
changes=[]
for name in ['xboxdash.xbe','evoxdash.xbe']:
    before=c.read(name);(art/('before-'+name)).write_bytes(before)
    action=restore(c,name,binary.read_bytes());changes.append(dict(path='C/'+name,before_sha256=m.sha(before),after_sha256=expected,action=action))
c.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(final)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(final)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(final)])).get('backing-filename')
with ColdIO(final) as io:
    rr=readers(io,final);c=m.Writer(io,m.fatx.open_partition(io,final,'C'))
    for name in ['xboxdash.xbe','evoxdash.xbe']:assert m.sha(c.read(name))==expected
    f=read(ws/'outputs/video-gpu-handoff216/fixture-control001.json')
    for name,digest in f['files'].items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
    assert 'xwninst218a' not in rr['F'].directory(1)['entries']
scan(final,art/'allocation');a=read(art/'allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(source)==original
(k/'fixture002.json').write_text(json.dumps(dict(prepared=True,parent_sha256=original,parent=str(source),fixture_sha256=sha(final),fixture_path_windows='E:/Codex-archive/xbox-windows-native/instance218/correlation002-source.qcow2',changes=changes,protected_files=f['files'],source_unchanged=True,no_windows_startup_or_driver_change=True,physical_access=False,guest_launch=False,scope='Disposable emulator-only boot-entry substitution to reviewed query app; preserve both original C binaries privately. No physical dashboard modification.'),indent=2)+'\n')
print('218 explicit stock-app fixture002 verified; no guest launch yet')
