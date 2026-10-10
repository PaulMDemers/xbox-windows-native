"""Review actual native capture without promoting it to Windows input support."""
import hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;read=lambda p:json.loads(p.read_text());p=read(k/'physical001.json')
assert p.get('collected_utc') and p['baseline_restored']
path=k/'physical001-review.json';assert not path.exists()
data=(k/p['log']['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==p['log']['sha256']
spec=importlib.util.spec_from_file_location('native_parser',k/'analyze.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=dict(physical_result=True,windows_input_qualified=False,baseline_exact=p['baseline_exact'],selected_files_checked=len(p['before']),dashboard_returned=True,windows_launched=False,full_allocation_audit=False)
try:
 d=m.parse(data);(k/'artifacts/physical001/decoded.json').write_text(json.dumps(d,indent=2)+'\n')
 r.update(native_capture_passed=d['native_capture_passed'] and d['mode']=='physical',device=d.get('device'),xid=d.get('xid'),xid_raw=d.get('xid_raw'),reports=len(d['reports']),distinct_reports=d['distinct_reports'],issues=d['issues'],transport_events=d['transport_events'],reported_failures=d['reported_failures'])
 decoded=[v['decoded'] for v in d['reports'] if 'decoded' in v]
 r['decoded_standard_reports']=len(decoded)
 if decoded:
  r['digital_button_values']=sorted({v['buttons'] for v in decoded})
  r['analog_ranges']={name:[min(v['analog'][name] for v in decoded),max(v['analog'][name] for v in decoded)] for name in decoded[0]['analog']}
  r['stick_ranges']=[[min(v['sticks'][i] for v in decoded),max(v['sticks'][i] for v in decoded)] for i in range(4)]
except (ValueError,KeyError,AssertionError) as e:r.update(native_capture_passed=False,parse_error=str(e))
path.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
