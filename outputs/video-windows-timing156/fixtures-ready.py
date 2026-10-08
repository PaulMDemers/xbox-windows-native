"""Seal both fixtures and identical guest inputs before any emulator starts."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];target=k/'fixtures-ready.json';assert not target.exists()
def read(p):return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
cases={};fixtures=[]
for case in ['control001','candidate001']:
    assert not (k/case/'runner-start.json').exists() and not (ws/('work/runs/nt5-vtime156-'+case)).exists()
    p=k/('fixture-'+case+'.json');f=read(p);fixtures.append(f)
    assert read(k/case/'preflight.json')['passed'] and read(k/case/'before-configuration.json')['expected_configuration']
    base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
    assert sha(base)==f['fixture_sha256']
    cases[case]=dict(fixture_manifest_sha256=sha(p),fixture_sha256=f['fixture_sha256'],preflight_sha256=sha(k/case/'preflight.json'))
for key in ['protected','preserved_hives','payloads','startup_sha256','parents','parent_manifest_sha256','inherited_configuration']:
    assert fixtures[0][key]==fixtures[1][key],key
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases=cases,
    same_guest_payloads=True,same_parent_and_chain=True,physical_access=False,debugger=False)
target.write_text(json.dumps(r,indent=2)+'\n')
(k/'pair-input-review.json').write_text(json.dumps(r,indent=2)+'\n')
print('Both fresh fixtures/preflights complete before either run')
