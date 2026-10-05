"""Owned direct-RAM emulator fixture with initially clean trace; no hardware access."""
import importlib,json,subprocess,sys,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'))
m=importlib.import_module('prepare-fixture')
base=ws/'outputs/native-windows-fatx-forensics/artifacts/gdi-baseline-003.qcow2'
expected=json.loads((ws/'outputs/video-next/probe-v3/fixture.json').read_text())['fixture_sha256']
assert m.filehash(base)==expected
assert json.loads((k/'compiled-tests.json').read_text())['passed']
m.target=base.with_name('video-direct-ram-001.qcow2');seed=ws/'work/video-direct-ram-001-seed.qcow2'
assert not m.target.exists() and not seed.exists()
assert shutil.disk_usage('/mnt/c').free>8*1024**3
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(m.target)],check=True)
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(m.target);w=m.Writer(io,m.fatx.open_partition(io,m.target,'F'))
payloads=[]
driver=(k/'artifacts/xboxvnt5.sys').read_bytes()
assert m.sha(driver)==json.loads((k/'compiled-tests.json').read_text())['sha256']
old=w.read('winnt/system32/drivers/xboxvnt5.sys')
assert m.sha(old)=='f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb'
trace=b'XWN-VID-TRACE01\n'+bytes(4080)
for path,data in [('winnt/system32/drivers/xboxvnt5.sys',driver),('winnt/system32/xwn-video-trace.bin',trace),
 ('Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd',b'@echo off\r\nC:\\xwnram01\\runner.exe\r\nexit\r\n')]:
    m.replace(w,path,data);payloads.append(dict(path=path,sha256=m.sha(data),bytes=len(data)))
review=json.loads((k/'build-review.json').read_text());assert review['passed']
runner=(k/'artifacts/runner.exe').read_bytes();probe=(ws/'outputs/video-next/probe-v3/artifacts/gdi-probe.exe').read_bytes()
assert m.sha(runner)==review['files'][0]['sha256'] and m.sha(probe)==review['files'][1]['sha256']
for path,data in [('xwnram01/runner.exe',runner),('xwnram01/replay.exe',probe),('xwnram02/replay.exe',probe)]:
    payloads.append(w.write(path,data))
w.flush()
for row in payloads:assert m.sha(w.read(row['path']))==row['sha256']
fatx=m.sha(w.read('winnt/system32/drivers/xwnfatx.sys'))
assert fatx=='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(m.target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(m.target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+m.target.name,str(seed)],check=True)
assert m.filehash(base)==expected
r=dict(scope=__doc__,source_sha256=expected,fixture_sha256=m.filehash(m.target),seed_sha256=m.filehash(seed),
       payloads=payloads,fatx_sha256=fatx,trace_sha256=m.sha(trace),initial_trace_clean=True,host_reset_between_boots=False,physical_access=False)
(k/'fixture.json').write_text(json.dumps(r,indent=2)+'\n');print('Verified isolated single-boot fixture starting with clean trace')
