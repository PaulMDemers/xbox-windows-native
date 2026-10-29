"""Compare independent 934-case executions of original versus compact native code."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((K/'model001.json').read_text());b=json.loads((K/'model002.json').read_text())
assert a['passed'] and b['passed'] and len(a['cases'])==len(b['cases'])==934
rows=[]
for x,y in zip(a['cases'],b['cases']):
 for key in ['name','raw_result','writes','ports','reads']:assert x[key]==y[key],(x['name'],key)
 rows.append(dict(name=x['name'],original_instructions=x['instructions'],compact_instructions=y['instructions'],
     original_critical=x['critical_instructions'],compact_critical=y['critical_instructions'],
     common_result_trace_sha256=hashlib.sha256(json.dumps({k:x[k] for k in ['raw_result','writes','ports','reads']},sort_keys=True).encode()).hexdigest()))
p=K/'equivalence001.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    physical_access=False,case_count=934,pins={n:sha(K/n) for n in ['model001.json','model002.json','compact001.json']},
    exact_register_reads_writes_ports_and_730_dword_results=True,cases=rows,
    limitations=['Instruction counts differ; no timing or physical hardware equivalence claim','Full bridge and CPU qualification still required']),indent=2)+'\n')
print('PASS934 original/compact exact result and device trace equivalence')
