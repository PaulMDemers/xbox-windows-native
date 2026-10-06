"""Rehearse the physical API-only probe with baseline0093 video and candidate0098 FATX."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
base=ws/'outputs/native-windows-fatx-forensics/artifacts/fatx-mapped-eof-fixed.qcow2'
ref=json.loads((k.parent/'fatx-mapped-eof/fixture-fixed.json').read_text());assert m.filehash(base)==ref['fixture_sha256']
target=base.with_name('fatx0098-physical-trial-rehearsal.qcow2');seed=ws/'work/fatx0098-physical-trial-rehearsal-seed.qcow2'
assert not target.exists() and not seed.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert m.sha(w.read('winnt/system32/drivers/xwnfatx.sys'))==ref['fatx_sha256']
video=(k.parent/'video-trace-reuse/artifacts/xboxvnt5.sys').read_bytes()
assert m.sha(video)=='3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf'
display=Path('/mnt/e/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/framebuf.dll').read_bytes()
assert m.sha(display)=='5da1fe7c3cdaf67a4a487c8872c2034fbc425bfd36d2b7715b2a1c4caa51df86'
payloads=[]
for path,data in [('winnt/system32/drivers/xboxvnt5.sys',video),('winnt/system32/framebuf.dll',display),('Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',b'@echo off\r\nC:\\xwneof98\\probe.exe\r\nexit\r\n')]:
    m.replace(w,path,data);payloads.append(dict(path=path,bytes=len(data),sha256=m.sha(data)))
payloads.append(w.write('xwneof98/probe.exe',(k/'artifacts/probe.exe').read_bytes()));w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in payloads:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(base)==ref['fixture_sha256']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r=dict(scope=__doc__,physical_access=False,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),parent_sha256=ref['fixture_sha256'],payloads=payloads,preserved_payloads=[],input_tails=[],fatx_sha256=ref['fatx_sha256'])
(k/'fixture-rehearsal.json').write_text(json.dumps(r,indent=2)+'\n');print('Physical API probe fixture prepared')
