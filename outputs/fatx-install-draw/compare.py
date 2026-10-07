"""Compare completed installer cases without promoting them to physical qualification."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
dest=k/'comparison.json';assert not dest.exists()
fixtures=[read(k/('fixture-'+c+'.json')) for c in ['001','002']]
maps=[{r['path']:r['sha256'] for r in f['payloads']+f['preserved_payloads']} for f in fixtures]
assert maps[0].keys()==maps[1].keys()
changed=[p for p in maps[0] if maps[0][p]!=maps[1][p]]
assert changed==['xwnidle/drawmode.txt']
assert maps[0][changed[0]]==sha(b'0') and maps[1][changed[0]]==sha(b'1')
assert fixtures[0]['parent_fixture_sha256']==fixtures[1]['parent_fixture_sha256']
assert fixtures[0]['preserved_during_drawing_staging']==fixtures[1]['preserved_during_drawing_staging']
review=read(k/'probe-review.json');rows=[];pins={}
for case,f in zip(['001','002'],fixtures):
 q=read(k/case/'qualification.json');d=read(k/case/'drawing-audit.json');al=read(k/case/'alignment.json');a=read(k/case/'audit.json')
 assert not q['physical_qualified'] and not q['ordinary_stability_qualified']
 assert next(p for p in a['payloads'] if p['path']=='xwnidle/probe.exe')['sha256']==review['probe_sha256']
 for name,digest in q['evidence_sha256'].items():assert sha((k/case/name).read_bytes())==digest
 pins[case]=sha((k/case/'qualification.json').read_bytes())
 rows.append(dict(case=case,passed=q['passed'],mode=d['mode'],drawing_protocol=d['protocol_passed'],warning_coverage=d['target_warning_coverage'],drawing_start=d.get('start'),drawing_end=d.get('end'),samples=d.get('samples'),target_offsets=al['actual_after_copy_offsets'],target_intact=al['target_warning_intact'],first111_exact=al['target_first111_exact'],new_log_bytes=al['new_bytes'],new_non_ascii_offsets=al['new_non_ascii_offsets'],normal_shutdown_count=a['normal_shutdown_count']))
r=dict(passed=all(v['passed'] for v in rows),physical_access=False,physical_qualified=False,ordinary_stability_qualified=False,parent_fixture_sha256=fixtures[0]['parent_fixture_sha256'],helper_sha256=review['probe_sha256'],only_changed_staged_payload=changed[0],qualification_sha256=pins,cases=rows,limits='Matched UI-assisted emulator diagnostics. Coverage brackets visible file growth during a worker lifetime, not exact syscall overlap, pixel correctness or performance. No physical source-buffer capture or explanation of its malformed prefix; disk sectors and timing differ.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
