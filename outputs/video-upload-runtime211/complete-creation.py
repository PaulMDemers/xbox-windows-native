"""Complete pre-probe factory metadata from reviewed compiled inputs before capture."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'creation-completion.json';assert not dest.exists() and not (k/'capture.json').exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=read(k/'creation.json');b=read(k/'build-review.json');assert r['passed'] and b['passed']
assert r['unchanged_runner_sha256']==b['binaries']['runner.exe']['sha256']==sha(k/'artifacts/runner.exe')
assert r['unchanged_wizard_sha256']==b['binaries']['wizard.exe']['sha256']==sha(k/'artifacts/wizard.exe')
assert read(k/'probe-build001.json')['binary_sha256']==b['binaries']['replay.exe']['sha256']==sha(k/'artifacts/replay.exe')
archive=k/'artifacts/pre-probe-creation.json';archive.write_bytes((k/'creation.json').read_bytes())
r['runner_sha256']=sha(k/'artifacts/runner.exe');r['probe_sha256']=sha(k/'artifacts/replay.exe')
(k/'creation.json').write_text(json.dumps(r,indent=2)+'\n')
dest.write_text(json.dumps(dict(passed=True,physical_access=False,guest_launch=False,prior_sha256=sha(archive),completed_sha256=sha(k/'creation.json'),
 build_review_sha256=sha(k/'build-review.json'),only_added_fields=['runner_sha256','probe_sha256'],
 limits='Factory ran before new probe existed. Complete two capture preflight fields from actual compiled/reviewed binary pins; no binary/source/fixture mutation.'),indent=2)+'\n')
print('Creation capture preflight fields completed from reviewed compiled binaries')
