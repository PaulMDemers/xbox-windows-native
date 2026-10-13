"""Replace only replay.exe in the fully reviewed never-executed recovered seed."""
import json,os,pathlib,shutil,subprocess,sys
K=pathlib.Path(__file__).resolve().parent;ws=K.parents[1]
sys.path.insert(0,str(K.parent/'video-text-oracle206'))
from common import ColdIO,readers,sha,save,hive,scan,m,HIVES
sys.path.insert(0,str(K.parent/'setup-wizard-automation201'))
from restore import restore
assert os.environ.get('XWN_BUILD_LEASE')=='held'
parent=json.loads((K.parent/'artifact-recovery329/seed001/fixture.json').read_text())
review=json.loads((K.parent/'artifact-recovery329/seed001/content-review002.json').read_text())
assert review['passed'] and review['source_sha256']==parent['fixture_sha256']
base=pathlib.Path(parent['fixture_path_linux']);assert sha(base)==parent['fixture_sha256']
out=K/'emu001';private=pathlib.Path('/mnt/e/xwn330/fixtures/emu001')
assert not out.exists() and not private.exists()
assert shutil.disk_usage('/mnt/c').free-64*1024**2>20*1024**3
assert shutil.disk_usage('/mnt/e').free-4*1024**3>20*1024**3
probe=pathlib.Path('/mnt/e/xwn327/build003/replay.exe')
pin=json.loads((K.parent/'hd-large327/build-review003.json').read_text())
assert pin['passed'] and sha(probe)==pin['binary_sha256']
with ColdIO(base) as io:
 rr=readers(io,base)
 for n,h in {**parent['files'],**parent['protected']}.items():
  v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 try:rr['F'].read(parent['namespace']+'/attempt.log')
 except KeyError:pass
 else:raise AssertionError('Consumed parent')
out.mkdir();art=out/'artifacts';art.mkdir();private.mkdir(parents=True)
target=private/'preparation.qcow2';source=private/'source.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
name='F/'+parent['namespace']+'/replay.exe'
restore(rr['F'],name[2:],probe.read_bytes())
for r in rr.values():r.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
assert not json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)])).get('backing-filename')
f=dict(parent);f['files']=dict(parent['files']);f['protected']=dict(parent['protected']);f['helpers']=dict(parent['helpers'])
f['files'][name]=f['protected'][name]=f['helpers']['replay.exe']=sha(probe)
with ColdIO(source) as io:
 rr=readers(io,source)
 for n,h in {**f['files'],**f['protected']}.items():
  v,p=n.split('/',1);assert m.sha(rr[v].read(p))==h,n
 for n in HIVES:
  p=art/('before-'+n);p.write_bytes(rr['F'].read('winnt/system32/config/'+n));hive(p)
scan(source,out/'before/artifacts')
a=json.loads((out/'before/allocation.json').read_text())
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==parent['fixture_sha256']
f.update(parent=str(base),parent_sha256=parent['fixture_sha256'],fixture_path_linux=str(source),
 fixture_path_windows='E:'+str(source)[6:],fixture_sha256=sha(source),case='emu001',
 replacement_files={name:sha(probe)},guest_launch=False,physical_access=False,
 limits='New327 large-area probe only on newly reviewed329 never-executed HD seed; no driver or setup-helper change. Historical317 container is not claimed byte-identical.')
save(out/'fixture.json',f)
print('Prepared330emu001; only327 replay executable differs')
