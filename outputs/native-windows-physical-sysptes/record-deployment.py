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
code/import audits and the 1343-event native trace passed. Both returning
guards preserve native registers/flags. Every PFN/color word and all 22702
system PTEs match independent models. Cache heads/tails/counts, original
loader descriptor restoration and preserved page mappings are verified.
Mapped-candidate, wrong-profile, corrupt PFN/descriptor/free-link/system-PTE
tests reject the altered state. Normal builds, parent-option checks and
patch series 0042 passed.

Uploaded '''+u['completed_utc']+'''. All 33 files verified by readback.
Three physical-tested XWNG90 files retained under xwng90 backup names.
The console was not remotely launched. Physical XWNY90 is pending.
'''
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'''The next candidate **XWNY90** finalizes PFN flags, restores the loader's
original descriptor extent and initializes system-PTE caches. It stops
before executive-pool initialization and process-page allocation. Emulator
validation passed; physical testing is pending. See the [system-PTE report](outputs/native-windows-physical-sysptes/REPORT.txt).

'''+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-freelist/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-sysptes/REPORT.txt)').replace('[patch-check-0041.json](outputs/native-windows-physical-freelist/patch-check-0041.json)','[patch-check-0042.json](outputs/native-windows-physical-sysptes/patch-check-0042.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [system-PTE candidate](../native-windows-physical-sysptes/REPORT.txt), patch 0042, verifies six PFN flag updates, original descriptor restoration and 22702 system PTEs, including 650 cache blocks. Both display modes, 1343-event tracing, code/import audits and corruption rejection passed in xemu. All 33 files were read back after upload; XWNG90 backups are retained. Physical **XWNY90** is pending. See [validation](../native-windows-physical-sysptes/validation.json) and [deployment](../native-windows-physical-sysptes/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNY90 pending.')
