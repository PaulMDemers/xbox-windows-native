"""Recheck actual compiler/dependency/donor inputs and prepared cold children."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'native-input-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
b=read(k/'build001.json');assert b['status']=='compiled';count=0
def pin(p,digest):
    global count
    assert sha(p)==digest,str(p);count+=1
ros=Path('/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1');old=Path('/home/paul/xbox-windows-native/build/video-shared-framebuffer-001/candidate001')
pin(ros/'i386/bin/i686-w64-mingw32-gcc',b['compiler_sha256']);pin(old/'host-tools/bin/pefixup',b['pefixup_sha256'])
for name,digest in b['dependency_pins'].items():pin(Path(name),digest)
for name,digest in b['copied_inputs'].items():pin(k/'artifacts/build001/inputs'/name,digest)
assert not b.get('thin_materialized'), 'Review any newly encountered thin libraries explicitly'
for row in b['builds']:pin(k/'artifacts/build001'/row['case']/'xboxbvid.dll',row['sha256'])
for case in ['control001','candidate001']:
    f=read(k/('fixture-'+case+'.json'));pin(Path(f['fixture_path_linux']),f['fixture_sha256']);pin(Path(f['parent']),f['parent_sha256'])
    a=read(k/('emu-'+case)/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
    assert f['device_policy']==read(k.parent/'video-upload-runtime211/fixture-candidate001.json')['device_policy']
h=read(k/'host-tests002.json');assert h['passed']
for row in h['runs']:pin(Path(row['command'][-1]),row['binary_sha256'])
dest.write_text(json.dumps(dict(passed=True,checks=count,source_sha256=sha(Path(__file__)),physical_access=False,guest_launch=False,
    limits='Recorded input/child hashes and cold allocation only; no clean full source build, runtime write guard or physical qualification.'),indent=2)+'\n')
print('Native frozen dependencies and both cold children verified:',count)
