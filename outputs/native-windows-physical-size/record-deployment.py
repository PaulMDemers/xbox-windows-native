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
s+='\nFinal validation: both display modes, old-HAL and changed-kernel rejection,\nfull code/import audits and the 46-checkpoint trace passed. The descriptor\nlist is unchanged and all target PDEs remain absent. Normal builds, parent\noption guard and the complete 34-patch source chain pass.\n\nUploaded '+u['completed_utc']+'. All 33 files verified by readback.\nThree physical-tested XWNS90 files retained under xwns90 backup names.\nThe console was not remotely launched. Physical XWNQ90 is pending.\n'
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]';assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNQ90** completes native pool and page-table sizing\nand stops before consuming descriptors or allocating page tables. Both\ndisplay modes and a 46-checkpoint trace pass in xemu; physical testing is\npending. See the [memory sizing report](outputs/native-windows-physical-size/REPORT.txt).\n\n'+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-scan/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-size/REPORT.txt)').replace('[patch-check-0033.json](outputs/native-windows-physical-scan/patch-check-0033.json)','[patch-check-0034.json](outputs/native-windows-physical-size/patch-check-0034.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [memory sizing candidate](../native-windows-physical-size/REPORT.txt), patch 0034, checks native pool sizes, PFN/color page count, candidate counters and the first planned page-table range. It halts before descriptor consumption or page-table allocation. Both display modes, rejection checks, code/import audits and the 46-checkpoint trace pass in xemu. All 33 files were verified after upload; XWNS90 backups are retained. Physical **XWNQ90** is pending. See [validation](../native-windows-physical-size/validation.json) and [deployment](../native-windows-physical-size/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNQ90 pending.')
