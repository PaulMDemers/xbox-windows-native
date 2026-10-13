"""Reconstruct the HD seed from its retained never-executed 251 ancestor."""
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
K=Path(__file__).resolve().parent
W=K.parents[1]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'))
from common import ColdIO, readers, sha, save, hive, scan, m, HIVES
sys.path.insert(0,str(W/'outputs/setup-wizard-automation201'))
from restore import restore
assert os.environ.get('XWN_BUILD_LEASE')=='held'
out=K/'seed001'
private=Path('/mnt/e/xwn329/seed001')
assert not out.exists() and not private.exists(), 'Consumed preparation'
assert shutil.disk_usage('/mnt/c').free-64*1024**2>20*1024**3
assert shutil.disk_usage('/mnt/e').free-4*1024**3>20*1024**3
parent=json.loads((W/'outputs/demo-integration251/emu001/fixture.json').read_text())
historical=json.loads((W/'outputs/hd-windows317/candidate001/fixture.json').read_text())
base=Path(parent['fixture_path_linux'])
assert sha(base)==parent['fixture_sha256']
archive=Path('/mnt/e/Codex-archive/xbox-windows-native/0.2.0-recovered329/xwn-0.2.0-hd-overlay.zip')
release=json.loads((W/'outputs/release-0.2.0/bundle.json').read_text())['archives'][0]
assert sha(archive)==release['sha256']
payload={}
with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
        if name.startswith('1080i/'):
            payload[name[len('1080i/'):]]=z.read(name)
payload['F/xwndemo251/wizard.exe']=Path('/mnt/e/xwn329/helper-restored001/wizard.exe').read_bytes()
assert len(payload)==7
for name,data in payload.items():
    assert m.sha(data)==historical['files'][name]
for field in ['files','protected']:
    merged=dict(parent[field]);merged.update({n:m.sha(b) for n,b in payload.items()})
    assert merged==historical[field],field
with ColdIO(base) as io:
    rr=readers(io,base)
    for name,h in {**parent['files'],**parent['protected']}.items():
        v,p=name.split('/',1);assert m.sha(rr[v].read(p))==h,name
    try: rr['F'].read(parent['namespace']+'/attempt.log')
    except KeyError: pass
    else: raise AssertionError('Seed contains consumed workload')
out.mkdir();private.mkdir(parents=True)
target=private/'preparation.qcow2';source=private/'source.qcow2'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;io=m.SliceIO(target);rr=readers(io,target)
changes={}
for name,data in payload.items():
    v,p=name.split('/',1);changes[name]=restore(rr[v],p,data)
for r in rr.values():r.flush()
subprocess.run(['qemu-img','convert','-c','-O','qcow2',str(target),str(source)],check=True)
subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(target),str(source)],check=True)
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(source)]))
assert not info.get('backing-filename')
subprocess.run(['qemu-img','check',str(source)],check=True)
hives={}
art=private/'artifacts';art.mkdir()
with ColdIO(source) as io:
    rr=readers(io,source)
    for name,h in {**historical['files'],**historical['protected']}.items():
        v,p=name.split('/',1);assert m.sha(rr[v].read(p))==h,name
    try: rr['F'].read(parent['namespace']+'/attempt.log')
    except KeyError: pass
    else: raise AssertionError('Unexpected consumed workload')
    for n in HIVES:
        p=art/('before-'+n);p.write_bytes(rr['F'].read('winnt/system32/config/'+n));hives[n]=hive(p)
scan(source,private/'before/artifacts')
a=json.loads((private/'before/allocation.json').read_text())
assert a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
assert sha(base)==parent['fixture_sha256']
digest=sha(source)
f=dict(historical)
f.update(parent=str(base),parent_sha256=parent['fixture_sha256'],fixture_path_linux=str(source),
         fixture_path_windows='E:'+str(source)[6:],fixture_sha256=digest,
         guest_launch=False,physical_access=False,reconstructed_from_251=True,
         original317_fixture_sha256=historical['fixture_sha256'],
         byte_identical_original317=digest==historical['fixture_sha256'],
         all_original317_file_and_protected_pins_exact=True,
         replacement_files={n:m.sha(b) for n,b in payload.items()},
         before_artifacts=str(art),limits='Fresh never-executed reconstruction from retained251; original317 disk hash comparison separately recorded.')
save(out/'fixture.json',f)
save(out/'review.json',dict(passed=True,changes=changes,hives=hives,allocation=a,
     byte_identical_original317=f['byte_identical_original317'],parent_unchanged=True,
     physical_access=False,guest_launch=False))
print(json.dumps(dict(passed=True,sha256=digest,byte_identical_original317=f['byte_identical_original317'],changes=changes)))
