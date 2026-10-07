"""Add a fresh sibling case002 after the first concurrency qualification; never reuse001."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
assert json.loads((k/'001/qualification.json').read_text())['passed']
assert not (k/'fixture-002.json').exists() and not (k/'repeat-enabled.json').exists()
for name in ['Run.ps1','supervise.py','trial.py','audit.py','audit-allocation.py','capture-timeout.py','decode-timeout.py','qualify.py','prepare-fixture.py']:
    p=k/name;s=p.read_text()
    s=s.replace("[ValidateSet('001')]","[ValidateSet('001','002')]")
    s=s.replace("case=='001'","case in ['001','002']").replace("in ['001']","in ['001','002']")
    if name=='prepare-fixture.py':
        s=s.replace("case=sys.argv[1];assert case in ['001','002']", "case=sys.argv[1];assert case in ['001','002']\nif case=='002':assert json.loads((k/'001/qualification.json').read_text())['passed']")
    p.write_text(s)
(k/'repeat-enabled.json').write_text(json.dumps({'scope':__doc__,'driver_changed':False,'helper_changed':False,'case001_overwritten':False,'parent':'same settled null001 image; independent writable fixture'},indent=2)+'\n')
