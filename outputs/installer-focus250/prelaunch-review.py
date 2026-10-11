"""Fail before resource/instance creation on absent static trace inputs."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'prelaunch-review001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
trace=(k/'trace.py').read_text();required=set(re.findall(r"k/'([^']+)'",trace));assert 'inventory001.json' in required
for name in required:assert (k/name).is_file(),name
assert sha(k/'inventory001.json')==sha(k.parent/'worker-barrier248/inventory001.json')
assert read(k/'diagnostic-test003.json')['passed'] and read(k/'source-review001.json')['exact_inverse_equals_parent']
build=read(k/'wizard-build001.json');assert sha(k/'wizard.c')==build['source_sha256'];assert sha(k/'artifacts/wizard-build001/wizard.exe')==build['binary_sha256']
old=read(k.parent/'worker-barrier248/fixture-preserve001.json');new=read(k/'fixture-preserve001.json')
changes=[n for n in old['files'] if old['files'][n]!=new['files'][n]];assert changes==['F/xwnret224/wizard.exe']
assert new['files'][changes[0]]==build['binary_sha256'];assert old['device_policy']==new['device_policy'] and not new['inherited_null_policy']
for p in k.glob('*.py'):ast.parse(p.read_text())
dest.write_text(json.dumps(dict(passed=True,static_trace_inputs=[dict(path=n,sha256=sha(k/n)) for n in sorted(required)],only_guest_file_changes=changes,policy_unchanged=True,emulator_changed=False,physical_access=False,prior249_windows_launch=False),indent=2)+'\n');print('250 static dependency/guest delta review PASS')
