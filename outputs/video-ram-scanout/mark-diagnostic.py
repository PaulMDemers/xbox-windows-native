"""Correct the copied preparation-only debugger label before freezing the run."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;p=k/'fixture-candidate001.json'
assert not (k/'candidate001/preflight.json').exists() and not (k/'preparation-record.json').exists()
raw=p.read_bytes();r=json.loads(raw);assert r['debugger'] is False
(k/'preparation-record.json').write_bytes(raw)
r['debugger']=True;r['ordinary_qualified']=False
r['preparation_record_sha256']=hashlib.sha256(raw).hexdigest()
r['diagnostic_note']='Metadata refinement before preflight; immutable fixture/seed bytes unchanged. trace.py must arm before launch. Preparation record retained.'
p.write_text(json.dumps(r,indent=2)+'\n')
