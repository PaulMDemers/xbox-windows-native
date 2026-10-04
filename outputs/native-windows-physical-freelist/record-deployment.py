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
full code/import audits and the 1333-event native trace passed. The returning
accounting guard preserves all native registers and flags. Every PFN/color
byte matches the independent model, with 20 loaded images protected.
The three native event calls return with PIC masks intact. Occupied-page,
wrong-profile, corrupt pre-walk PFN, unexpected descriptor and corrupt
post-walk list-link tests all reject the altered state. Normal builds,
parent option checks and patch series 0041 passed.

Uploaded '''+u['completed_utc']+'''. All 33 files verified by readback.
Three physical-tested XWNJ90 files retained under xwnj90 backup names.
The console was not remotely launched. Physical XWNG90 is pending.
'''
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'''The next candidate **XWNG90** runs the complete native descriptor walk to
build free-page lists and mark reserved pages in use. It checks every PFN
and color-list word, preserves all 20 loaded images and stops before the
remaining MM initialization. Emulator validation passed; physical testing
is pending. See the [free-page list report](outputs/native-windows-physical-freelist/REPORT.txt).

'''+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-pfncommit/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-freelist/REPORT.txt)').replace('[patch-check-0040.json](outputs/native-windows-physical-pfncommit/patch-check-0040.json)','[patch-check-0041.json](outputs/native-windows-physical-freelist/patch-check-0041.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [free-page list candidate](../native-windows-physical-freelist/REPORT.txt), patch 0041, preserves the validated descriptor guard and allows the native free/in-use PFN walk, then halts before remaining MM initialization. Every PFN/color byte, protected image and expected event state is checked. Both display modes, code/import audits, 1333-event tracing and pre/post-walk corruption rejection passed in xemu. All 33 files were read back after upload; XWNJ90 backups are retained. Physical **XWNG90** is pending. See [validation](../native-windows-physical-freelist/validation.json) and [deployment](../native-windows-physical-freelist/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNG90 pending.')
