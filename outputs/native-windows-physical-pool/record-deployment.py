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
s+='\nFinal validation: both display modes, old-HAL and changed-kernel rejection,\nfull code/import audits and the 1115-event trace passed. Every pool PTE\nwrite was checked before and after execution. An injected alias to the\nfirst pool frame was rejected before any allocation; all 532 proposed\nframes and descriptors remained unchanged. Normal builds, the parent-option\nguard and the source series through patch 0036 passed. The first trace\nattempt counted a breakpoint twice; the debugger sequencing was fixed\nand the trace rerun successfully, without changing the diagnostic.\n\nUploaded '+u['completed_utc']+'. All 33 files verified by readback.\nThree physical-tested XWNA90 files retained under xwna90 backup names.\nThe console was not remotely launched. Physical XWNO90 is pending.\n'
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNO90** maps 504 initial nonpaged-pool pages, then\nhalts before pool initialization and PFN setup. Both display modes and\nan instruction trace pass in xemu; physical testing is pending. See the\n[pool mapping report](outputs/native-windows-physical-pool/REPORT.txt).\n\n'+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-pt/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-pool/REPORT.txt)').replace('[patch-check-0035.json](outputs/native-windows-physical-pt/patch-check-0035.json)','[patch-check-0036.json](outputs/native-windows-physical-pool/patch-check-0036.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [pool mapping candidate](../native-windows-physical-pool/REPORT.txt), patch 0036, checks all 532 allocation frames, allows the 28 page tables and 504 pool PTEs, then halts before pool initialization. Both display modes, rejection checks, code/import audits and the 1115-event trace pass in xemu. An injected alias to the first pool frame is rejected before allocation. All 33 files were verified after upload; XWNA90 backups are retained. Physical **XWNO90** is pending. See [validation](../native-windows-physical-pool/validation.json) and [deployment](../native-windows-physical-pool/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNO90 pending.')
