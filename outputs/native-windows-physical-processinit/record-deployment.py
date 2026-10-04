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
s+='\nFinal validation: both display modes, 1358-event native trace, code/import\naudits and four injected-corruption tests passed. Unsafe process inputs,\nchanged process data, a dirty hash page and corrupt PFN data are rejected.\nOld HAL and changed kernel are rejected before entry. Normal builds, parent\noption check and patch series 0044 passed.\n\nUploaded '+u['completed_utc']+'. All 33 files verified by readback.\nThree previous XWNZ90 files retained under xwnz90 backup names.\nPhysical XWNW90 testing is pending; no remote launch was performed.\n';p.write_text(s)
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNW90** lets native process address-space initialization\nreturn, then verifies the process/thread state, working-set and hash pages,\nand all PFN records. It stops before further MM initialization and storage.\nEmulator checks passed; it is uploaded for physical testing.\n\n'+needle).replace('[latest diagnostic](outputs/native-windows-physical-processpages/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-processinit/REPORT.txt)').replace('[patch-check-0043.json](outputs/native-windows-physical-processpages/patch-check-0043.json)','[patch-check-0044.json](outputs/native-windows-physical-processinit/patch-check-0044.json)');p.write_text(s)
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [process-initialization candidate](../native-windows-physical-processinit/REPORT.txt), patch 0044, halts after native MmInitializeProcessAddressSpace returns successfully. All PFNs, working-set/hash pages and process/thread state are checked. Both display modes, a 1358-event trace, code/import audits and four corruption tests passed in xemu. All 33 files were read back after upload; XWNZ90 backups are retained. Physical **XWNW90** is pending. See [validation](../native-windows-physical-processinit/validation.json) and [deployment](../native-windows-physical-processinit/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle));print('Deployment recorded; physical XWNW90 pending.')
