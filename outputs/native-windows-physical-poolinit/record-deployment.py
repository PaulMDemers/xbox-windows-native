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
s+='\nFinal validation: both display modes, old-HAL and changed-kernel rejection,\nfull code/import audits and the 1120-event native trace passed. The full\n2064384-byte pool comparison permits only the expected 507 header/link\nDWORD updates. All pool lists, ownership links and expansion PTEs match\nthe independent model. An injected alias to the first pool frame and an\nunexpected must-succeed size are rejected before allocation, preserving\nall 532 candidate frames and the descriptor list. Normal builds, the\nparent-option guard and the source series through patch 0037 passed.\n\nUploaded '+u['completed_utc']+'. All 33 files verified by readback.\nThree physical-tested XWNO90 files retained under xwno90 backup names.\nThe console was not remotely launched. Physical XWNU90 is pending.\n'
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNU90** completes native nonpaged-pool initialization\nand its expansion-PTE setup, then stops before PFN backing allocation.\nBoth display modes, the complete pool-write comparison and rejection tests\npass in xemu; physical testing is pending. See the\n[pool initialization report](outputs/native-windows-physical-poolinit/REPORT.txt).\n\n'+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-pool/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-poolinit/REPORT.txt)').replace('[patch-check-0036.json](outputs/native-windows-physical-pool/patch-check-0036.json)','[patch-check-0037.json](outputs/native-windows-physical-poolinit/patch-check-0037.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [pool initialization candidate](../native-windows-physical-poolinit/REPORT.txt), patch 0037, checks the initial pool lists, all 500 free-page owner fields, four must-succeed links and 5432 expansion PTEs. Both display modes, rejection checks, code/import audits, a full pool-memory write comparison and the 1120-event trace pass in xemu. All 33 files were verified after upload; XWNO90 backups are retained. Physical **XWNU90** is pending. PFN backing allocation, storage and desktop remain beyond this stop. See [validation](../native-windows-physical-poolinit/validation.json) and [deployment](../native-windows-physical-poolinit/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNU90 pending.')
