"""Fresh standalone child; only inherited224 wizard diagnostic differs from239 seed."""
import contextlib,shutil,subprocess
from common import *
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'));from restore import restore
f=read(k.parent/'worker-barrier248/fixture-preserve001.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
root=Path('/mnt/e/Codex-archive/xbox-windows-native/phase249');root.mkdir(exist_ok=False)
target=root/'seed001-preparation.qcow2';source=root/'seed001-source.qcow2'
build=read(k/'wizard-build001.json');binary=k/'artifacts/wizard-build001/wizard.exe';assert sha(binary)==build['binary_sha256']
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;rr=readers(m.SliceIO(target),target)
for name,digest in f['files'].items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
for name in ['wizard201.log','result.log','retirement.log']:
 try:rr['F'].read('xwnret224/'+name)
 except KeyError:pass
 else:raise AssertionError('Namespace not fresh')
restore(rr['F'],'xwnret224/wizard.exe',binary.read_bytes())
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)])).get('backing-filename')
f['files']['F/xwnret224/wizard.exe']=f['protected']['F/xwnret224/wizard.exe']=build['binary_sha256']
with ColdIO(source) as io:
 after=readers(io,source)
 for name,digest in f['files'].items():v,p=name.split('/',1);assert m.sha(after[v].read(p))==digest,name
 for name in HIVES:assert m.sha(after['F'].read('winnt/system32/config/'+name))==f['files']['F/winnt/system32/config/'+name]
scan(source,k/'seed001/artifacts');a=read(k/'seed001/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
f.update(fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/phase249/'+source.name,fixture_sha256=sha(source),seed_sha256=sha(source),parent=str(base),parent_sha256=sha(base),seed_owner='outputs/installer-focus249/seed001',new_unique_runtime='nt5-phase249-preserve001',diagnostic_guest_change='F/xwnret224/wizard.exe wait-only telemetry; exact policy/input/idle/timeout retained',emulator_source_changed=False,matched_control_scope='Closed247/248 comparison only, not paired qualification')
save(k/'fixture-preserve001.json',f)
print('249 fresh standalone seed cold-readback verified')
