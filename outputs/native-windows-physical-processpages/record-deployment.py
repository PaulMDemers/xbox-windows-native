from pathlib import Path
import json
kit=Path(__file__).resolve().parent;root=kit.parent.parent
u=json.loads((kit/'ftp-upload.json').read_text());v=json.loads((kit/'validation.json').read_text())
assert u['completed_utc'] and not u['launched'] and 'error' not in u
assert len(u['files'])==3 and len(u['unchanged_files_verified'])==30
assert all(f['final_name_verified'] and f['staging_readback_equal'] for f in u['files'])
v.update(installed_on_physical_console=True,uploaded_utc=u['completed_utc'],physical_tested=False)
(kit/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
p=kit/'REPORT.txt';s=p.read_text();assert 'Final validation:' not in s
s+='\nFinal validation: both display modes, 1353-event native trace, code/import\naudits and five corruption tests passed. Mapped-candidate and wrong-profile\nguards reject unsafe inputs. Old HAL and modified kernel are rejected before\nentry. Normal builds, parent-option check and patch series 0043 passed.\n\nUploaded '+u['completed_utc']+'. All 33 package files verified. Three\nprior XWNY90 files retained under xwny90 backup names. No remote launch.\nPhysical XWNZ90 test is pending.\n';p.write_text(s)
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNZ90** initializes executive-pool descriptors and\nallocates/zeros the first process page table and working-set page. It stops\nbefore working-set publication and process initialization. Emulator checks\npassed; the candidate is uploaded and physical testing is pending.\n\n'+needle).replace('[latest diagnostic](outputs/native-windows-physical-sysptes/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-processpages/REPORT.txt)').replace('[patch-check-0042.json](outputs/native-windows-physical-sysptes/patch-check-0042.json)','[patch-check-0043.json](outputs/native-windows-physical-processpages/patch-check-0043.json)');p.write_text(s)
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [first process-page candidate](../native-windows-physical-processpages/REPORT.txt), patch 0043, initializes executive-pool descriptors and allocates/zeros two native pages. It halts before working-set publication. Both display modes, a 1353-event trace, code/import audits and corruption tests passed in xemu. All 33 files were read back after upload; XWNY90 backups are retained. Physical **XWNZ90** is pending. See [validation](../native-windows-physical-processpages/validation.json) and [deployment](../native-windows-physical-processpages/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle));print('Deployment recorded; physical XWNZ90 pending.')
