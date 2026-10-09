"""Preserve the pre-connection capture001 host refusal; generate capture002 only."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=k/'capture002.py';refusal=k/'capture001-host-refusal.json'
assert not out.exists() and not refusal.exists() and not (k/'capture.json').exists()
creation=json.loads((k/'creation.json').read_text())
for name,field in [('runner.exe','runner_sha256'),('gdi-probe.exe','probe_sha256')]:
    assert sha(k/'artifacts'/name)==creation[field]
assert not (k/'artifacts/F').exists() and not (k/'artifacts/E').exists()
refusal.write_text(json.dumps(dict(stage='capture001',source_sha256=sha(k/'capture.py'),
    error='FileExistsError [WinError 183]: artifacts already exists',
    physical_access=False,physical_writes=False,launch_attempted=False,
    cause='Fresh kit pre-copied exact runner/probe into artifacts before capture.mkdir(exist_ok=False).'),indent=2)+'\n')
text=(k/'capture.py').read_text()
text=text.replace("art=k/'artifacts';art.mkdir(exist_ok=False)","""art=k/'artifacts';assert art.is_dir()
creation=json.loads((k/'creation.json').read_text())
for name,field in [('runner.exe','runner_sha256'),('gdi-probe.exe','probe_sha256')]:
    assert hashlib.sha256((art/name).read_bytes()).hexdigest()==creation[field]
assert not (art/'F').exists() and not (art/'E').exists()""")
out.write_text(text,encoding='utf-8',newline='\n')
print('Capture001 refusal preserved; unique corrected capture002 prepared')
