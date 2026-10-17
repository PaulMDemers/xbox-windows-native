"""Freeze actual new control dependencies after the read-only baseline audit."""
import hashlib,json,shutil,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'preflight001.json';assert not out.exists()
prep=json.loads((K/'ntfs-preparation001.json').read_text())
cold=json.loads((K/'ntfs-cold0-002.json').read_text());assert cold['complete'] and cold['audit_unchanged'] and cold['source_unchanged']
assert sha(Path(prep['path'])/'disk.qcow2')==cold['disk_sha256']==prep['child_sha256']
assert sha(Path(prep['source']))==prep['source_sha256']
manifest=json.loads((Path(cold['private_path'])/'manifest.json').read_text())
assert not any(n.startswith('xwn440/') for n in manifest)
modules=json.loads((W/'outputs/crypto-path425/modules001.json').read_text())['modules']
for dll in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll']:
 assert manifest['winnt/system32/'+dll]['sha256']==modules[dll],dll
assert json.loads((K/'binary-review001.json').read_text())['passed']
files=list(K.glob('*.py'))+[K/'runner.c',W/'tools/graphics_present.py',W/'tools/build_space.py']
files += [W/'outputs'/n for n in ['crypto-persistence423/ntfs_read002.py','fatx-mapped-eof/coldio.py','clean-media404/pc-run001.py','clean-media404/hive_audit004.py','clean-media404/raw_value004.py','native-windows-physical-f/decode-legacy-events.py']]
files += [Path(shutil.which(n)) for n in ['qemu-img','qemu-nbd']]
for root in [W/'work/python-packages/Registry',Path('/mnt/e/xwn423/ntfs-python001'),Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages/hivex')]:
 files += [p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
offline=Path('/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib')
files += list((offline/'python3/dist-packages').glob('libhivexmod*.so'))+list((offline/'x86_64-linux-gnu').glob('libhivex.so*'))
pins={str(p):sha(p) for p in files}
for p,h in prep['runtime_pins'].items():assert sha(Path(p))==h;pins[p]=h
for p,h in prep['inputs'].items():assert sha(K/p)==h,p
record=dict(passed=True,files=pins,fixture_os_exports_match=True,mode='PC Cirrus, no hardware qualification',cold_scope=cold['scope'],floppy_sha256=prep['floppy_sha256'])
out.write_text(json.dumps(record,indent=2)+'\n');print('Pinned dependencies:',len(pins))
