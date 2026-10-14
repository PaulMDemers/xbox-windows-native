"""Final byte/provenance review of the source candidate; no hardware access."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import zipfile

K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
report=K/'final-review.json'
if report.exists():raise RuntimeError('Consumed review')
src=read(K/'source003.json')
for path,h in src['input_sha256'].items():
    if sha((W/path).read_bytes())!=h:raise RuntimeError('401 input changed: '+path)
old=read(W/'outputs/demo-integration399/frozen.json')
for path,h in old.items():
    if sha((W/path).read_bytes())!=h:raise RuntimeError('399 frozen input changed: '+path)
replay=read(K/'portable-replay001.json');tests=read(K/'tool-tests001.json')
if not replay['passed'] or len(replay['components'])!=6 or not tests['passed']:raise RuntimeError('Validation incomplete')
root=K/'export';spec=importlib.util.spec_from_file_location('verify',root/'tools/verify-package.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);verified=v.verify(root)
for p in root.rglob('*'):
    if p.is_file() and p.read_bytes()!=(Path('C:/xwn401/source003')/p.relative_to(root)).read_bytes():
        raise RuntimeError('Repository export differs: '+str(p))
package=read(K/'package001.json')
for archive in package['archives']:
    p=Path(archive['path'])
    if sha(p.read_bytes())!=archive['sha256']:raise RuntimeError('Archive changed')
    with zipfile.ZipFile(p) as z:
        for name in z.namelist():
            if z.read(name)!=(root/name).read_bytes():raise RuntimeError('Archive/export mismatch')
pycount=0
for p in K.rglob('*.py'):
    ast.parse(p.read_text(encoding='utf-8-sig'));pycount+=1
staged=subprocess.check_output(['git','-C',str(W),'diff','--cached','--name-only','--','outputs/public-source401']).decode().splitlines()
for name in staged:
    if subprocess.check_output(['git','-C',str(W),'show',':'+name])!=(W/name).read_bytes():
        raise RuntimeError('Staged bytes changed: '+name)
value=dict(passed=True,source_components=6,export_manifest=verified,
           export_files=verified['verified_files']+1,archives=package['archives'],
           frozen401_inputs=len(src['input_sha256']),frozen399_inputs=len(old),
           syntax_files=pycount,byte_exact_staged_kit_files=len(staged),
           tool_guard_tests=tests['count'],private_history_scan=read(K/'history001.json')['counts_unique_blobs_per_category'],
           public_ready=False,hardware_access=False,compiled=False,
           scope='Source/tree/transport/package evidence only; no license clearance or complete build qualification')
with report.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({key:value[key] for key in ['passed','source_components','export_files','frozen401_inputs','frozen399_inputs','byte_exact_staged_kit_files']}))
