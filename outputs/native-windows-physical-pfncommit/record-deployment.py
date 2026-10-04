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
full code/import audits and the 1324-event native trace passed. The final
descriptor list covers all 64 MiB together with the 623 consumed frames;
all PFN/color bytes and mappings match the independent model. Occupied
candidate and incompatible pool-size tests block allocation. Corrupted
PFN data and an unexpected descriptor count both prevent reconciliation.
Normal builds, parent option checks and patch series 0040 passed.

Uploaded '''+u['completed_utc']+'''. All 33 files verified by readback.
Three physical-tested XWNL90 files retained under xwnl90 backup names.
The console was not remotely launched. Physical XWNJ90 is pending.
'''
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'''The next candidate **XWNJ90** reconciles the native descriptor update on
our pinned memory layout, restoring 622 pages omitted by a repeated
subtraction. It validates mappings, page records and the original extent,
then halts before free-page lists. Emulator validation passed; physical
testing is pending. See the [descriptor accounting report](outputs/native-windows-physical-pfncommit/REPORT.txt).

'''+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-pfnmap/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-pfncommit/REPORT.txt)').replace('[patch-check-0039.json](outputs/native-windows-physical-pfnmap/patch-check-0039.json)','[patch-check-0040.json](outputs/native-windows-physical-pfncommit/patch-check-0040.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [descriptor accounting candidate](../native-windows-physical-pfncommit/REPORT.txt), patch 0040, validates the native second commit and restores 622 omitted pages on the pinned single-candidate path. It stops before free lists or storage. Both display modes, code/import and memory audits, native tracing, corrupted-PFN and unexpected-descriptor rejection passed in xemu. All 33 files were read back after upload; XWNL90 backups are retained. Physical **XWNJ90** is pending. See [validation](../native-windows-physical-pfncommit/validation.json) and [deployment](../native-windows-physical-pfncommit/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNJ90 pending.')
