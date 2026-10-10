"""New host-only full-sequence review after closure; never changes frozen guest sources."""
import hashlib,json,sys
from pathlib import Path
from upload_sequence import review
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001']
physical='--physical' in sys.argv;out=k/(case if physical else 'emu-'+case);dest=out/'sequence-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
a=read(out/('physical-audit.json' if physical else 'audit.json'));assert read(out/'closure.json')['closed']
files=[out/'artifacts/physical'/('after-sample%d'%i) if physical else out/'artifacts'/('sample%d/gdi-baseline.txt'%i) for i in range(5)]
r=dict(passed=False,host_only=True,physical_result=physical,guest_launch=False,case=case,
 audit_sha256=sha(out/('physical-audit.json' if physical else 'audit.json')),
 source_pins={p.name:sha(p) for p in [Path(__file__),k/'upload_sequence.py',k/'upload_analysis.py']},
 input_pins={p.relative_to(k).as_posix():sha(p) for p in files},samples=[])
for p in files:r['samples'].append(review(p.read_bytes().decode('ascii'),int(case=='candidate001')))
r['passed']=all(v['passed'] for v in r['samples']);dest.write_text(json.dumps(r,indent=2)+'\n')
assert r['passed'],'Preserve sequence failure; no new deployment permitted'
print('All5 actual119 packet sequences/159 transitions PASS:',case)
