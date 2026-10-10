"""Fresh213 immutable children of the CLOSED211 prelaunch seed, no physical IO."""
import subprocess
from common import *
sys.path.insert(0,str(k.parent/'setup-wizard-automation201'));from restore import restore
case=sys.argv[1];assert case in ['control001','candidate001']
out=k/('emu-'+case);assert not out.exists()
review=read(k/'build-review.json');assert review['passed']
f=read(k.parent/'video-upload-runtime211/fixture-candidate001.json');base=Path(f['fixture_path_linux'])
assert sha(base)==f['fixture_sha256']
root=Path('/mnt/e/Codex-archive/xbox-windows-native/staging213')
target=root/(case+'-preparation.qcow2');source=root/(case+'-source.qcow2')
assert not target.exists() and not source.exists()
out.mkdir();art=out/'artifacts';art.mkdir();root.mkdir(exist_ok=True)
files=dict(f['files']);protected=dict(f['protected'])
namespace='xwnst213a' if case=='control001' else 'xwnst213b'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
for name,digest in files.items():v,p=name.split('/',1);assert m.sha(rr[v].read(p))==digest,name
for name in ['runner.exe','replay.exe','wizard.exe']:
 p=k.parent/'video-upload-runtime211/artifacts'/name
 expected=read(k.parent/'video-upload-runtime211/build-review.json')['binaries'][name]['sha256'];assert sha(p)==expected
 rr['F'].write(namespace+'/'+name,p.read_bytes());files['F/'+namespace+'/'+name]=expected;protected['F/'+namespace+'/'+name]=expected
binary=k/'artifacts/build003'/case/'xboxvnt5.sys';assert sha(binary)==review['binaries'][case]['sha256']
path='winnt/system32/drivers/xboxvnt5.sys';restore(rr['F'],path,binary.read_bytes())
files['F/'+path]=sha(binary);protected['F/'+path]=sha(binary)
startup=('@echo off\r\nC:\\'+namespace+'\\runner.exe /emulator\r\nexit\r\n').encode('ascii')
restore(rr['F'],STARTUP,startup);files['F/'+STARTUP]=m.sha(startup)
for reader in rr.values():reader.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]));assert not info.get('backing-filename')
with ColdIO(source) as io:
 after=readers(io,source)
 for name,digest in files.items():v,p=name.split('/',1);assert m.sha(after[v].read(p))==digest,name
 for name in HIVES:
  p=art/('before-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name));hive(p)
scan(source,out/'before/artifacts');a=read(out/'before/allocation.json')
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==f['fixture_sha256']
save(k/('fixture-'+case+'.json'),dict(case=case,prepared=True,namespace=namespace,files=files,protected=protected,
 parent=str(base),parent_sha256=f['fixture_sha256'],fixture_path_linux=str(source),
 fixture_path_windows='E:/Codex-archive/xbox-windows-native/staging213/'+source.name,fixture_sha256=sha(source),seed_sha256=sha(source),
 physical_access=False,guest_launch=False,inherited_null_policy=False,
 device_policy=f['device_policy'],gpu_submission=False,
 limits='Captured physical-core211 policy, HAL/FATX/bootvid/display unchanged. Only new213 miniport probe and fresh helper/startup paths. Buffer probe OFF/ON; not GPU, physical, dump or speed qualification.'))
print('Fresh213 standalone prepared/cold checked:',case)
