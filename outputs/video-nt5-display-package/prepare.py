"""Stage matching original display INF and existing binaries into a new owned child."""
import importlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
parent=ws/'outputs/native-windows-fatx-forensics/artifacts/video-installer-pair004.qcow2'
r=json.loads((ws/'outputs/video-installer-isolation/pair004/fixture.json').read_text())
parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
review=json.loads((k/'build-review.json').read_text());assert review['passed']
assert shutil.disk_usage('/mnt/c').free>8*1024**3
target=parent.with_name('video-nt5-display-package-001.qcow2');seed=ws/'work/video-nt5-display-package-001-seed.qcow2'
assert not target.exists() and not seed.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
system=w.read('winnt/system32/config/system')
payloads={v['path']:v for v in r['payloads']}
for row in payloads.values():assert m.sha(w.read(row['path']))==row['sha256']
files={'xwninf01/install.exe':(k/'artifacts/install.exe').read_bytes(),
       'xwninf01/xboxvnt5.inf':(k/'xboxvnt5.inf').read_bytes(),
       'xwninf01/xboxvnt5.sys':w.read('winnt/system32/drivers/xboxvnt5.sys'),
       'xwninf01/framebuf.dll':w.read('winnt/system32/framebuf.dll')}
assert m.sha(files['xwninf01/install.exe'])==review['installer_sha256']
assert m.sha(files['xwninf01/xboxvnt5.inf'])==review['inf_sha256']
for path,data in files.items():payloads[path]=w.write(path,data)
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
data=b'@echo off\r\nstart "" C:\\xwninf01\\install.exe\r\nexit\r\n';m.replace(w,startup,data)
payloads[startup]=dict(path=startup,sha256=m.sha(data),bytes=len(data));w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in payloads.values():assert m.sha(fresh.read(row['path']))==row['sha256']
assert fresh.read('winnt/system32/config/system')==system
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,parent_fixture_sha256=parent_hash,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         payloads=list(payloads.values()),system_unchanged_during_staging=True,
         limits='Inherits diagnostic FAILEDINSTALL flags for unsupported01B0/01B4 only. GPU not suppressed. Same0096/0097 binaries; no hardware access.')
(k/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n');print('Package fixture verified')
