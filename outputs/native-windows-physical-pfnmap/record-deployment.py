from pathlib import Path
import json
kit=Path(__file__).resolve().parent;root=kit.parent.parent
u=json.loads((kit/'ftp-upload.json').read_text());v=json.loads((kit/'validation.json').read_text())
assert u['completed_utc'] and not u['launched'] and 'error' not in u
assert len(u['files'])==3 and len(u['unchanged_files_verified'])==30
assert all(f['final_name_verified'] and f['staging_readback_equal'] for f in u['files'])
v.update(installed_on_physical_console=True,uploaded_utc=u['completed_utc'],physical_tested=False)
(kit/'validation.json').write_text(json.dumps(v,indent=2)+'\n',newline='\n')
p=kit/'REPORT.txt';s=p.read_text();assert 'Final validation:' not in s
s+='''
Final validation: both display modes, old-HAL and changed-kernel rejection,
full code/import audits and the 1323-event native trace passed. All PFN and
color bytes match the independent model before and after the native TLB
flush. Original mappings have only expected permission changes. An occupied
candidate and incompatible pool size halt before allocation; a corrupted
unused PFN word is rejected before free-page lists. Normal builds, parent
option checks and the source series through patch 0039 passed.

Uploaded '''+u['completed_utc']+'''. All 33 files verified by readback.
Three physical-tested XWNE90 files retained under xwne90 backup names.
The console was not remotely launched. Physical XWNL90 is pending.
'''
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'''The next candidate **XWNL90** initializes mapped-page PFN records and color
heads, then returns from the native TLB flush. It stops before free-page
list construction. Both display modes, the complete page-record model,
execution trace and rejection tests pass in xemu; physical testing is
pending. See the [mapped PFN report](outputs/native-windows-physical-pfnmap/REPORT.txt).

'''+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-pfn/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-pfnmap/REPORT.txt)').replace('[patch-check-0038.json](outputs/native-windows-physical-pfn/patch-check-0038.json)','[patch-check-0039.json](outputs/native-windows-physical-pfnmap/patch-check-0039.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [mapped PFN candidate](../native-windows-physical-pfnmap/REPORT.txt), patch 0039, initializes mapped-page records and color heads, then stops after the native TLB flush and before free-page lists. Both display modes, the full PFN/color model, code/import audits, a 1323-event trace and corrupted-record rejection pass in xemu. All 33 files were read back after upload; XWNE90 backups are retained. Physical **XWNL90** is pending. Storage and the desktop remain beyond this stop. See [validation](../native-windows-physical-pfnmap/validation.json) and [deployment](../native-windows-physical-pfnmap/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNL90 pending.')
