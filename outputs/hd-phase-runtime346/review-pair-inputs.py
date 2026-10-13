"""Require identical fixture contracts except matched driver bytes/host case paths."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;dest=K/'pair-input-review.json';assert not dest.exists()
load=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a,b=[load(K/c/'fixture.json') for c in ['control001','candidate001']]
assert a['parent']==b['parent'] and a['parent_sha256']==b['parent_sha256'] and a['namespace']==b['namespace']
diffs={}
for field in ['files','protected']:
    assert a[field].keys()==b[field].keys();diff=[p for p in a[field] if a[field][p]!=b[field][p]]
    assert diff==['E/winnt/system32/xwnown.dll'],diff;diffs[field]=diff
for h in ['system','software','default','sam','security']:
    assert (K/'control001/artifacts'/('before-'+h)).read_bytes()==(K/'candidate001/artifacts'/('before-'+h)).read_bytes()
for c in ['control001','candidate001']:
    assert load(K/c/'preparation.json')['prepared'] and load(K/c/'before-allocation/allocation.json')['allocation_consistent']
    assert (K/c/'artifacts/before-system').stat().st_size>0
dest.write_text(json.dumps(dict(passed=True,same_immutable_parent=a['parent_sha256'],matched_fixture_differences=diffs,all_five_hives_identical=True,physical_access=False,inputs={str(p.relative_to(K)):sha(p) for c in ['control001','candidate001'] for p in [K/c/'fixture.json',K/c/'preparation.json']}),indent=2)+'\n')
print('Matched same-parent fixtures; only driver payload differs')
