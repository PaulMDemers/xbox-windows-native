"""Owned installer-queue diagnostic child; no physical access or PnP state edits."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
base=ws/'outputs/native-windows-fatx-forensics/artifacts/video-direct-map-002.qcow2'
ref=json.loads((k.parent/'video-direct-map-settled/fixture.json').read_text());assert m.filehash(base)==ref['fixture_sha256']
target=base.with_name('shutdown-installer-trace-001.qcow2');seed=ws/'work/shutdown-installer-trace-001-seed.qcow2'
assert not target.exists() and not seed.exists()
probe=(k.parent/'shutdown-diagnostics/artifacts/probe.exe').read_bytes()
assert m.sha(probe)=='431b6b862aab6f8eb72aef9a342f3e8fd79515b104055c28d64c12483320aefb'
fatx=(k.parent/'fatx-paging-eof/artifacts/xwnfatx.sys').read_bytes()
assert m.sha(fatx)=='beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd'
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
unchanged={p:m.sha(w.read(p)) for p in ['winnt/system32/config/'+n for n in ['system','software','default','sam','security']]+['winnt/system32/drivers/xboxvnt5.sys','winnt/system32/framebuf.dll']}
old_fatx=m.sha(w.read('winnt/system32/drivers/xwnfatx.sys'));assert old_fatx==ref['fatx_sha256']
payloads=[]
for path,data in [('Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',b'@echo off\r\nC:\\xwnsd01\\probe.exe\r\nexit\r\n'),('winnt/system32/drivers/xwnfatx.sys',fatx)]:
    m.replace(w,path,data);payloads.append(dict(path=path,sha256=m.sha(data),bytes=len(data)))
payloads.append(w.write('xwnsd01/probe.exe',probe));w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in payloads:assert m.sha(fresh.read(row['path']))==row['sha256']
for p,h in unchanged.items():assert m.sha(fresh.read(p))==h
assert m.filehash(base)==ref['fixture_sha256']
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r=dict(scope=__doc__,physical_access=False,fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),parent_sha256=ref['fixture_sha256'],payloads=payloads,unchanged=unchanged,previous_fatx_sha256=old_fatx,fatx_sha256=m.sha(fatx),limits='Older installer-queue fixture retains video0096 and its original device settings. Only FATX is advanced from0088 to the verified0098 EOF fix; diagnostic startup/helper added. Not a physical clone or ordinary qualification.')
(k/'fixture-001.json').write_text(json.dumps(r,indent=2)+'\n');print('Owned installer trace fixture prepared')
