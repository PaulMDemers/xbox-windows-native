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
s+='\nFinal validation: both display modes, old-HAL and changed-kernel rejection,\nfull code/import audits and the 105-event trace passed. The trace watches\neach native PDE write and each cleared page. The injected mapped-candidate\ntest is rejected before allocation with candidate bytes and descriptors\nunchanged. Normal builds, the parent-option guard and the complete source\nseries through patch 0035 pass. One initial standard-display fixture launch\nfailed at dashboard FTP before loading the diagnostic; its fresh rerun\npassed. The mapped-candidate test was rerun with paused physical-memory\ncapture after its final debugger read timed out; the rerun passed.\n\nUploaded '+u['completed_utc']+'. All 33 files verified by readback.\nThree physical-tested XWNQ90 files retained under xwnq90 backup names.\nThe console was not remotely launched. Physical XWNA90 is pending.\n'
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNA90** permits the first 28 native page-table\nallocations, with checks before and after the loop. Emulator validation\nincludes each page write and refusal to use a mapped candidate; physical\ntesting is pending. See the [page-table report](outputs/native-windows-physical-pt/REPORT.txt)\nand [boot-screen milestones](outputs/native-windows-physical-pt/BOOT-PROGRESS.txt).\n\n'+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-size/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-pt/REPORT.txt)').replace('[patch-check-0034.json](outputs/native-windows-physical-size/patch-check-0034.json)','[patch-check-0035.json](outputs/native-windows-physical-pt/patch-check-0035.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [first page-table candidate](../native-windows-physical-pt/REPORT.txt), patch 0035, checks every active mapping before permitting 28 native page-table allocations, then checks cleared pages, allocation counters and unchanged unrelated state. Both display modes, rejection checks, code/import audits and the 105-event trace pass in xemu. An injected alias to a candidate frame is rejected before allocation. All 33 files were verified after upload; XWNQ90 backups are retained. Physical **XWNA90** is pending. See [validation](../native-windows-physical-pt/validation.json) and [deployment](../native-windows-physical-pt/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNA90 pending.')
