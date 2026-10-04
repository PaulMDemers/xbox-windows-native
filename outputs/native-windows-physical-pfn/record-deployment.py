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
s+='''
Final validation: both display modes, old-HAL and changed-kernel rejection,
full code/import audits and the 1317-event native trace passed. All 91 new
backing pages are zero, the exact descriptor transition matches, and both
IRQL round trips retain PIC ffff. An injected alias to the last color frame
and an unexpected must-succeed size stop before allocation, preserving all
623 candidate frames and the original descriptor list. Normal builds,
the parent-option guard and the source series through patch 0038 passed.

Uploaded '''+u['completed_utc']+'''. All 33 files verified by readback.
Three physical-tested XWNU90 files retained under xwnu90 backup names.
The console was not remotely launched. Physical XWNE90 is pending.
'''
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'''The next candidate **XWNE90** allocates and clears 90 PFN-database pages
and one color-table page, then stops before populating those structures.
Both display modes, allocation tracing and rejection checks pass in xemu;
physical testing is pending. See the
[PFN backing report](outputs/native-windows-physical-pfn/REPORT.txt).

'''+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-poolinit/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-pfn/REPORT.txt)').replace('[patch-check-0037.json](outputs/native-windows-physical-poolinit/patch-check-0037.json)','[patch-check-0038.json](outputs/native-windows-physical-pfn/patch-check-0038.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [PFN backing candidate](../native-windows-physical-pfn/REPORT.txt), patch 0038, allocates and zeroes 90 PFN-database pages plus one color-table page. The complete 1317-event trace, both display modes, all memory/code/import audits and rejection tests pass in xemu. All 33 files were read back after upload; XWNU90 backups are retained. Physical **XWNE90** is pending. PFN/color population, storage and desktop remain beyond this stop. See [validation](../native-windows-physical-pfn/validation.json) and [deployment](../native-windows-physical-pfn/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNE90 pending.')
