"""Preserve complete new event meanings separately from scoped boot evidence."""
import datetime,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'event-review001.json';assert not out.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=read(K/'stage001.json');c=read(K/'collection001.json');a=read(K/'cold-review001.json')
n='/E/winnt/system32/config/sysevent.evt';b=Path(s['before'][n]['path']).with_name('sysevent.evt-review472.json');p=Path(c['files'][n]['path']).with_name('sysevent.evt-review472.json')
before=read(b)['records'];after=read(p)['records'];boundary=max(x['record'] for x in before);new=[x for x in after if x['record']>boundary]
assert [x['record'] for x in new]==list(range(595,603))
assert [x['record'] for x in new]==[x['record'] for x in a['events']['sysevent.evt']['new_records']]
popups=[x for x in new if x['source']=='Application Popup'];assert len(popups)==2
for x in popups:assert x['strings']==['rundll32.exe - DLL Initialization Failed','The application failed to initialize because the window station is shutting down. ']
assert new[-1]['source']=='EventLog' and new[-1]['event_id']==6006
assert all(x['generated_unix']<=new[-1]['generated_unix'] for x in popups)
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),strict_system_qualification=False,
 scoped_boot_and_selected_cold_audit_passed=True,new_system_records=new,new_application_records=0,
 shutdown_popup_initiator_unknown=True,windows_F_warning_not_dashboard_F=True,
 partition_mapping_basis='Historical462/463 mapping: Windows F corresponds to dashboard C. No new raw partition mapping or console C access.',
 no_event_suppression=True,no_repair_or_cleanup=True,input_hashes={str(f):sha(f) for f in [b,p,K/'cold-review001.json',K/'collection001.json']})
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(strict=False,new_records=len(new),shutdown_popups=len(popups))))
