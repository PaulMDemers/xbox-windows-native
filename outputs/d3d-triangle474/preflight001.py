"""Freeze actual new control dependencies after the read-only baseline audit."""
import hashlib,json,shutil,sys,time
from launch_gate import publish
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'preflight001.json';assert not out.exists()
prep=json.loads((K/'ntfs-preparation001.json').read_text())
cold=json.loads((K/'ntfs-cold0-002.json').read_text());assert cold['complete'] and cold['audit_unchanged'] and cold['source_unchanged']
assert sha(Path(prep['path'])/'disk.qcow2')==cold['disk_sha256']==prep['child_sha256']
assert sha(Path(prep['source']))==prep['source_sha256']
manifest=json.loads((Path(cold['private_path'])/'manifest.json').read_text())
assert not any(n.startswith('xwn474/') for n in manifest)
modules=json.loads((W/'outputs/crypto-path425/modules001.json').read_text())['modules']
for dll in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll']:
 assert manifest['winnt/system32/'+dll]['sha256']==modules[dll],dll
assert json.loads((K/'binary-review001.json').read_text())['passed']
sample=json.loads((K/'sample-build001.json').read_text())
assert sample['exit_code']==0 and sha(W/'src/samples/graphics-ladder/triangle.c')==sample['source_sha256']
assert sample['compiler_sha256']=='8ab0685d97b322aad3c37fd362b26fa5b9408ff6dd55a536c0a2d48de1c22b18'
files=list(K.glob('*.py'))+[K/'runner.c',K/'oracle-tests001.json',W/'tools/graphics_triangle.py',W/'tools/graphics_discovery.py',W/'tools/build_space.py']
files += [W/'outputs'/n for n in ['crypto-persistence423/ntfs_read002.py','fatx-mapped-eof/coldio.py','clean-media404/pc-run001.py','clean-media404/hive_audit004.py','clean-media404/raw_value004.py','native-windows-physical-f/decode-legacy-events.py']]
files += [Path(shutil.which(n)) for n in ['qemu-img','qemu-nbd']]
for root in [W/'work/python-packages/Registry',Path('/mnt/e/xwn423/ntfs-python001'),Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages/hivex')]:
 files += [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
offline=Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib')
files += list((offline/'python3/dist-packages').glob('libhivexmod*.so'))+list((offline/'x86_64-linux-gnu').glob('libhivex.so*'))
files += [K/n for n in ['ntfs-preparation001.json','ntfs-cold0-002.json','build001.json','sample-build001.json','binary-review001.json','inherited-gate-tests001.json']]
files += [W/'src/samples/graphics-ladder/triangle.c',W/'src/samples/graphics-ladder/triangle.cmd',W/'tools/build-graphics-samples.py',W/'tests/test_graphics_triangle.py']
pins={str(p.resolve()):sha(p) for p in files}
for p,h in prep['runtime_pins'].items():assert sha(Path(p))==h;pins[p]=h
for p,h in prep['inputs'].items():assert sha(K/p)==h,p
gate=json.loads((K/'inherited-gate-tests001.json').read_text());assert gate['passed'] is True and gate['gate_sha256']==sha(K/'launch_gate.py')
prior=json.loads((K.parent/'lifecycle453/independent001.json').read_text());assert manifest['winnt/system32/ddraw.dll']['sha256']==next(r['sha256'] for r in prior['rows'] if r['path']=='winnt/system32/ddraw.dll')
record=dict(schema=1,attempt='d3d-triangle474-pc001',fixture=str(Path(prep['path']).resolve()),completed=True,passed=True,finished_ns=time.time_ns(),files=pins,
 fixture_files={str(Path(prep['path'])/'disk.qcow2'):prep['child_sha256'],str(Path(prep['path'])/'probe.img'):prep['floppy_sha256'],prep['source']:prep['source_sha256']})
publish(out,record);print('Completed preflight published:',len(pins),'dependencies')
