"""Fresh pre-execution258 child, unchanged driver and259 renderer-only probe."""
import os,subprocess
from common import *
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert read(k/'renderer-build001.json')['passed'] and read(k/'attestation-review002.json')['passed']
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'));from restore import restore
f=read(k.parent/'surface-pattern258/emu001/fixture.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
out=k/'emu001';out.mkdir(exist_ok=False);art=out/'artifacts';art.mkdir()
root=Path('/mnt/e/Codex-archive/xbox-windows-native/bridge260');root.mkdir(exist_ok=False)
target=root/'emu001-preparation.qcow2';source=root/'emu001-source.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;rr=readers(m.SliceIO(target),target)
for name,digest in f['files'].items():
 v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
for name in ['xwnpat258/result.log','xwnpat259/result.log','xwnret224/result.log','xwnret224/wizard201.log']:
 try:rr['F'].read(name)
 except KeyError:pass
 else:raise AssertionError('Fresh namespace required')
binary=k.parent/'surface-renderer259/artifacts/build001/probe.exe'
assert sha(binary)==read(k.parent/'surface-renderer259/probe-review001.json')['native_sha256']
name='xwnpat259/probe.exe';rr['F'].write(name,binary.read_bytes());f['files']['F/'+name]=f['protected']['F/'+name]=sha(binary)
old=rr['F'].read(STARTUP);needle=b'C:\\xwnpat258\\probe.exe\r\n';assert old.count(needle)==1
startup=old.replace(needle,b'C:\\xwnpat259\\probe.exe\r\n')
restore(rr['F'],STARTUP,startup);f['files']['F/'+STARTUP]=m.sha(startup)
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)])).get('backing-filename')
with ColdIO(source) as io:
 after=readers(io,source)
 for name,digest in f['files'].items():
  v,p=name.split('/',1);assert m.sha(after[v].read(p))==digest,name
 for n in HIVES:
  data=after['F'].read('winnt/system32/config/'+n);assert m.sha(data)==f['files']['F/winnt/system32/config/'+n]
  p=art/('before-'+n);p.write_bytes(data);hive(p)
scan(source,out/'before/artifacts');a=read(out/'before/allocation.json');assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
f.update(fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/bridge260/'+source.name,
 fixture_sha256=sha(source),seed_sha256=sha(source),parent=str(base),parent_sha256=sha(base),debugger=True,
 ordinary_qualified=False,physical_access=False,new_unique_runtime='nt5-bridge260-emu001',
 compiled_emulator_from='E:/Codex-archive/xbox-windows-native/bridge260-build001',
 diagnostic_guest_change='Replace invocation of258 CPU baseline with259 renderer protocol; unchanged258 driver and224 workload',
 host_vram_preservation=True,physical_baseline_equivalent=False,
 inherited_emulator_policy='Historical250/258 synthetic null-device/unsupported-device policy retained; not current audio-integrated physical demo')
save(out/'fixture.json',f);print('260 fresh diagnostic fixture cold readback/allocation PASS; never launched by preparation')
