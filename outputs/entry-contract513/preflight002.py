"""Pin all inputs and reviewed read-only transport before the unique runtime."""
import ast,hashlib,json,shutil,socket
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'emu001';out=O/'preflight002.json'
assert not out.exists() and not (O/'runner-start.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for parent,name in [('entry-runtime505','host001.json'),('entry-runtime505','host003.json'),('entry-runtime505','host004.json'),('return-transport506','host002.json'),('return-transport506','host003.json')]:
 result=json.loads((K.parent/parent/name).read_text());assert result['passed']
 evidence=result.get('source_sha256',result.get('sources',{}))
 if isinstance(evidence,str):assert sha(K.parent/parent/'contracts.py')==evidence
 else:
  for filename,h in evidence.items():assert sha(K.parent/parent/filename)==h
for name in ['contracts.py','kernel_calls.py','indicator_calls.py','protocol003.py','entry_decode.py']:
 assert (K/name).read_bytes().replace(b'XWNBoot510a',b'XWNBoot504a')==(K.parent/'entry-runtime505'/name).read_bytes()
for name in ['probe.py','waiter.py']:
 assert (K/name).read_bytes()==(K.parent/'return-transport506'/name).read_bytes()
assert json.loads((K/'source-review001.json').read_text())['passed']
host=json.loads((K/'host001.json').read_text());assert host['passed']
for n,h in host['sources'].items():assert sha(K/n)==h
assert json.loads((K/'host002.json').read_text())['passed']
assert json.loads((K/'host003.json').read_text())['passed']
for name in ['host004.json','host005.json','host006.json']:
 result=json.loads((K/name).read_text());assert result['passed']
 evidence=result['source_sha256']
 if isinstance(evidence,str):assert sha(K/'contracts.py')==evidence
 else:
  for n,h in evidence.items():assert sha(K/n)==h
for p in K.glob('*.py'):ast.parse(p.read_text())
assert (K/'entry_decode.py').read_bytes()==(K.parent/'entry-receipt498/decode.py').read_bytes()
trace=(K/'trace001.py').read_text()
assert '192.168.' not in trace and trace.count('f.sendcmd(')==1
assert "g.ask('P" not in trace and "g.ask('M" not in trace
assert "'firmware-return-entry'" in (K/'indicator_calls.py').read_text()
for port in [6134,6135,6136,6137]:
 with socket.socket() as s:s.bind(('127.0.0.1',port))
capacity={drive:shutil.disk_usage(drive+':/').free for drive in ['C','E']}
assert capacity['C']-768*1024**2>=20*1024**3
old=json.loads((K.parent/'cromwell-devices414/emu001/frozen.json').read_text())
paths={W/p for p in old if (W/p).is_file()}
paths.update(p for p in K.glob('*.*') if p.is_file())
paths.update(K.parent/'release-readiness403'/n for n in ['stock_io002.py','analyze-allocation002.py'])
paths.update(K.parent/'surface-bridge260'/n for n in ['atomic_json.py'])
paths.update(K.parent/'entry-trampoline510'/n for n in ['build001.json','review002.json'])
paths.update(K.parent/'return-transport506'/n for n in ['host002.json','host003.json','probe.py','waiter.py'])
paths.update(K.parent/'entry-runtime505'/n for n in ['host001.json','host003.json','host004.json','kernel_calls.py','indicator_calls.py','contracts.py','trace001.py'])
pins={p.relative_to(W).as_posix():sha(p) for p in sorted(paths)}
external=[Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts')/n for n in ['with_xbox_resource.ps1','complete_xemu_instance.ps1','fatx_stage_boot.py']]
external.extend(Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib').glob('*.ps1'))
external += [Path(p) for p in ['C:/nxdk/lib/xboxkrnl/xboxkrnl.h','C:/xwn510/build001/default.xbe','C:/xwn513/preparation001/seed.qcow2','C:/xwn466/preparation001/seed.qcow2','C:/Emulators/xemu/system/bios/Complex_4627.bin','C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin','E:/xwn289/fixture001/hd.bin','E:/xwn329/retained-builds001/xemu-hd322.exe']]
external += [W/'outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso']
prior=json.loads((K.parent/'entry-runtime511/emu001/trace.json').read_text());external.extend(Path(r['private_file']) for r in prior['reads'])
hostpins={str(p):sha(p) for p in external}
archive=Path('C:/xwn513/frozen001');assert not archive.exists();archive.mkdir()
for name,h in pins.items():
 dest=archive/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/name,dest);assert sha(dest)==h
for name,data in [('frozen.json',pins),('host-dependencies.json',hostpins)]:
 (O/name).write_bytes((json.dumps(data,indent=2)+'\n').encode())
r=dict(passed=True,frozen_inputs=len(pins),external_dependencies=len(hostpins),capacity_bytes=capacity,projected_C_bytes=768*1024**2,minimum_free_bytes=20*1024**3,no_E_allocation=True,physical_access=False,read_only_debugger=True,actual_kernel_contract_not_yet_executed=True)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
