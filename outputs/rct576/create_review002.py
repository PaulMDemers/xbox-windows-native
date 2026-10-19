"""Preserve CRLF parser failure and write corrected supplemental offline reviews."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent
for old,new in [('capture_review001.py','capture_review002.py'),('review001.py','review002.py')]:
 p=K/new;assert not p.exists()
 s=(K/old).read_text().replace(".decode('ascii')",".decode('ascii').replace('\\r\\n','\\n')")
 s=s.replace('capture-review001.json','capture-review002.json').replace("out=K/'review001.json'","out=K/'review002.json'")
 s=s.replace('runner_fields=fields,physical_access=True','runner_fields=fields,capture_rows=actual,physical_access=True')
 p.write_bytes(s.encode())
p=K/'review-parser-failure001.json';assert not p.exists()
p.write_text(json.dumps(dict(failure='Physical runner decoded without universal newline normalization; anchored regex missed CRLF capture lines',incorrect_field='review001 capture_calls_succeeded false from empty parse',retained_records=['review001.json','capture-review001.json'],remedy='New review002 and capture_review002 normalize CRLF before anchored parsing; old source/evidence untouched',preparation_failure='First inline preparation command rejected by PowerShell quoting before Python ran; no files or evidence overwritten',guest_relaunch=False,cold_recollection=False),indent=2)+'\n')
