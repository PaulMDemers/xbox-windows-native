"""Fresh CPU baseline child; same historical250 policies and workload, no renderer test."""
import os,subprocess
from common import *
assert os.environ.get('XWN_BUILD_LEASE')=='held'
assert read(k/'build-review002.json')['passed']
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'));from restore import restore
f=read(k.parent/'installer-focus250/fixture-preserve001.json');base=Path(f['fixture_path_linux']);assert sha(base)==f['fixture_sha256']
out=k/'emu001';out.mkdir(exist_ok=False);art=out/'artifacts';art.mkdir()
root=Path('/mnt/e/Codex-archive/xbox-windows-native/pattern258');root.mkdir(exist_ok=False)
target=root/'cpu001-preparation.qcow2';source=root/'cpu001-source.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;rr=readers(m.SliceIO(target),target)
for name,digest in f['files'].items():
 v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
for name in ['xwnpat258/result.log','xwnret224/result.log','xwnret224/wizard201.log']:
 try:rr['F'].read(name)
 except KeyError:pass
 else:raise AssertionError('Fresh namespace required')
for n in ['pattern.sys','probe.exe']:
 binary=k/'artifacts/build002'/n;assert sha(binary)==read(k/'build002.json')['native'][n]['sha256']
 name='xwnpat258/'+n;rr['F'].write(name,binary.read_bytes());f['files']['F/'+name]=f['protected']['F/'+name]=sha(binary)
old=rr['F'].read(STARTUP);needle=b'C:\\xwnret224\\probe.exe\r\n';assert old.count(needle)==1
startup=old.replace(needle,b'C:\\xwnpat258\\probe.exe\r\nif errorlevel 1 exit /b 96\r\n'+needle)
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
f.update(fixture_path_linux=str(source),fixture_path_windows='E:/Codex-archive/xbox-windows-native/pattern258/'+source.name,fixture_sha256=sha(source),seed_sha256=sha(source),parent=str(base),parent_sha256=sha(base),debugger=False,ordinary_qualified=False,physical_access=False,new_unique_runtime='nt5-pattern258-emu001',compiled_emulator_from='outputs/xemu-cpu-surface-evict/build003',diagnostic_guest_change='Add dedicated CPU arena driver/probe before unchanged224 workload; inherited250 policy/hives untouched',host_vram_preservation=False)
save(out/'fixture.json',f);print('258 CPU fixture cold readback/allocation PASS')
