"""Compare event signatures without overriding any qualification gate."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
q=json.loads((k/'qualification.json').read_text())
prior=json.loads((k/'before-system-events.json').read_text())['records']
emulator=json.loads((k/'eligibility.json').read_text())['unresolved_emulator_popups']
fields=['source','event_id','type','strings','data_hex']
same=lambda a,b:all(a[n]==b[n] for n in fields)
r=dict(scope=__doc__,warnings=[],popups=[],strict_gate_unchanged=True)
for v in q['unexpected_errors']:
    r['warnings'].append(dict(event=v,exact_prior_record_matches=[p['record'] for p in prior if same(v,p)]))
for v in q['popups']:
    r['popups'].append(dict(event=v,exact_prior_physical_record_matches=[p['record'] for p in prior if same(v,p)],exact_emulator_signature_matches=[p['record'] for p in emulator if same(v,p)]))
r['limits']='Matching text/data establishes recurrence, not root cause or harmlessness. Physical popup remains a failed strict gate. Guest timestamps are not assumed to match host UTC.'
(k/'event-comparison.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
