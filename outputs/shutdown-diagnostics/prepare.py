"""Fresh emulator-only diagnostic child; all drivers and registry hives unchanged."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
base=ws/'outputs/native-windows-fatx-forensics/artifacts/fatx0098-soak-rehearsal.qcow2'
ref=json.loads((k.parent/'fatx0098-soak/fixture-rehearsal.json').read_text());assert m.filehash(base)==ref['fixture_sha256']
target=base.with_name('shutdown-diagnostics-001.qcow2');seed=ws/'work/shutdown-diagnostics-001-seed.qcow2'
assert not target.exists() and not seed.exists()
review=json.loads((k/'probe-review.json').read_text());assert review['passed']
probe=(k/'artifacts/probe.exe').read_bytes();assert m.sha(probe)==review['probe_sha256']
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
unchanged={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/config/default','winnt/system32/drivers/xwnfatx.sys','winnt/system32/drivers/xboxvnt5.sys','winnt/system32/framebuf.dll']}
startup='Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd';data=b'@echo off\r\nC:\\xwnsd01\\probe.exe\r\nexit\r\n'
m.replace(w,startup,data);payloads=[dict(path=startup,sha256=m.sha(data),bytes=len(data)),w.write('xwnsd01/probe.exe',probe)]
w.flush();fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in payloads:assert m.sha(fresh.read(row['path']))==row['sha256']
for p,h in unchanged.items():assert m.sha(fresh.read(p))==h
assert m.filehash(base)==ref['fixture_sha256']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r=dict(scope=__doc__,physical_access=False,fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),parent_sha256=ref['fixture_sha256'],payloads=payloads,unchanged=unchanged,fatx_sha256=ref['fatx_sha256'],limits='Existing synthetic resource model and inherited fixture device settings; not a physical machine clone or driver qualification.')
(k/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n');print('Diagnostic fixture prepared')
