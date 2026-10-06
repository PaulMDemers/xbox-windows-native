"""Summarize SetupAPI attempts and cold event results; no inferred process lifetimes."""
import json
from pathlib import Path
k=Path(__file__).resolve().parent
rows=[]
for case in ['001','002','003','004']:
 a=json.loads((k/case/'audit.json').read_text());p=json.loads((k/case/'package-audit.json').read_text())
 attempts=[];heading=None
 for line in p['new_setupapi_lines']:
  if line.startswith('['):heading=line
  if line.startswith('Munged cmdline: rundll32.exe newdev.dll,DevInstall '):
   attempts.append(dict(setupapi_heading=heading,command=line.split(': ',1)[1]))
 shutdowns=[dict(record=e['record'],generated_unix=e['generated_unix']) for e in a['new_events']['system'] if e['source']=='EventLog' and e['event_id']==6006]
 rows.append(dict(case=case,installer_attempts=attempts,popup_records=a['popup_records'],shutdowns=shutdowns,
  dashboard_return=a['dashboard_return'],workload_passed=a['probe_completed'],package_and_workload_passed=p['combined_checks_passed']))
r=dict(scope=__doc__,physical_access=False,cases=rows,
 limits='SetupAPI headings document log entries, not process creation/exit times. No root cause, popup owner or physical-device assignment is inferred. Cases002-004 are independent replays of one installed state, not three consecutive reboots.')
(k/'installer-event-comparison.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
