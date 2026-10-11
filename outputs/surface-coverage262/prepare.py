"""Read-only verify261 never-executed standalone seed for a NEW262 runtime copy."""
from common import *
import subprocess
parent=k.parent/'surface-residency261';f=read(parent/'emu001/fixture.json')
base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(base)]));assert not info.get('backing-filename')
out=k/'emu001';assert not out.exists();out.mkdir();art=out/'artifacts';art.mkdir()
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,digest in f['files'].items():
        v,path=name.split('/',1);assert m.sha(rr[v].read(path))==digest,name
    for path in ['xwnpat259/result.log','xwnret224/result.log','xwnret224/wizard201.log','xwnret224/retirement.log']:
        try:rr['F'].read(path)
        except KeyError:pass
        else:raise AssertionError('Seed has workload result: '+path)
    for n in HIVES:
        p=art/('before-'+n);p.write_bytes(rr['F'].read('winnt/system32/config/'+n));hive(p)
scan(base,out/'before/artifacts');a=read(out/'before/allocation.json')
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
f.update(new_unique_runtime='nt5-coverage262-emu001',reused_immutable_preexecution_seed=True,
    source_fixture_record=str(parent/'emu001/fixture.json'),compiled_emulator_from='E:/Codex-archive/xbox-windows-native/coverage262-build001',
    emulator_source_changed_only=read(k/'renderer-build001.json')['changed_sources'],
    diagnostic_guest_change='None relative to261 prepared seed: identical header-locked261 probe,258 held arena,224 workload.',
    runtime_change='262 bounded telemetry only; site11=4096, other sites256; includes pinned orderly-close helper')
assert sha(base)==f['fixture_sha256'];save(out/'fixture.json',f)
print('262 immutable seed cold readback and allocation verified; no guest launched')
