"""Separate unchanged large-pixel/timing checks from known primary coverage failure."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'candidate001';dest=out/'functional-scope001.json';assert not dest.exists()
sys.path.insert(0,str(K.parent/'hd-phase344'));from phase_analysis import analyze
samples=[]
for i in range(5):
    p=out/f'artifacts/sample{i}/gdi-baseline.txt';lines=p.read_text().splitlines();rows=[v.split() for v in lines]
    checks=[v for v in rows if v[0]=='LARGE_PIXEL_CHECK'];assert len(checks)==30
    for id in range(15):assert len([v for v in checks if v[1]==str(id) and v[3]=='1'])==2
    projected='\n'.join(v for v in lines if not v.startswith('PRIMARY348_'))
    old=analyze(projected,1);assert old['passed']
    samples.append(dict(index=i,log_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pixel_checks=30,legacy_large_checks_passed=True,intervals=len(old['intervals'])))
r=dict(functional_scope_passed=True,original_primary_coverage_gate_still_failed=True,ordinary_qualified=False,performance_qualified=False,samples=samples,scope='Read-only projection for separate original pixel/phase scope. Does not replace full350/349 qualifiers or bypass their failed primary gate.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('150 actual large pixel checks and75 legacy intervals passed; full primary gate stays failed')
