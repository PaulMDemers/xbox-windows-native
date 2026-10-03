from pathlib import Path
import json
kit=Path(__file__).resolve().parent;root=kit.parent.parent
u=json.loads((kit/'ftp-upload.json').read_text());v=json.loads((kit/'validation.json').read_text())
assert u['completed_utc'] and not u['launched'] and 'error' not in u
assert len(u['files'])==3 and len(u['unchanged_files_verified'])==30
assert all(f['final_name_verified'] and f['staging_readback_equal'] for f in u['files'])
v['installed_on_physical_console']=True;v['uploaded_utc']=u['completed_utc'];v['physical_tested']=False
(kit/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
p=kit/'REPORT.txt';s=p.read_text();assert 'Final validation:' not in s
s+='\nFinal validation: both display modes, old-HAL rejection, altered-kernel\nrejection and the native 44-checkpoint trace passed. The trace observes\nnative PDE clearing and high HAL entry, with RAM scanning, four partition\nhandlers and 17 loaded driver entries excluded. All 1388 imports and core\nexecutable sections pass the final memory audit. The original five bytes\nare restored; all 512 low PDEs are non-present and the high framebuffer\nalias has the expected physical pages and cache attributes. Normal builds,\nthe parent-option guard and the complete source patch chain also pass.\n\nUploaded '+u['completed_utc']+'. All 33 files verified by readback.\nThree physical-tested XWND90 files retained under xwnd90 backup names.\nThe console was not remotely launched. Physical XWNV90 is pending.\n'
p.write_text(s,newline='\n')
p=root/'README.md';s=p.read_text();needle='See [hardware status]'
assert s.count(needle)==1
s=s.replace(needle,'The next candidate **XWNV90** moves diagnostic output into the high HAL,\nexecutes native low-mapping removal and stops before RAM descriptor scanning.\nBoth display modes and the native trace pass in xemu; physical testing is\npending. See the [mapping-transition report](outputs/native-windows-physical-map/REPORT.txt).\n\n'+needle)
s=s.replace('[latest diagnostic](outputs/native-windows-physical-mi/REPORT.txt)','[latest diagnostic](outputs/native-windows-physical-map/REPORT.txt)').replace('[patch-check-0031.json](outputs/native-windows-physical-mi/patch-check-0031.json)','[patch-check-0032.json](outputs/native-windows-physical-map/patch-check-0032.json)')
p.write_text(s,newline='\n')
p=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=p.read_text();needle='2. Record video cable/adapter';assert s.count(needle)==1
paragraph='The [low-mapping transition candidate](../native-windows-physical-map/REPORT.txt), patch 0032, moves the checkpoint and display into the HAL and allows native clearing of all 512 low PDEs. It flushes translations and halts before RAM descriptor scanning. Both display modes, wrong-HAL/kernel rejection, code/import audits and a 44-checkpoint trace pass in xemu. All 33 files were verified after upload; XWND90 backups are retained. Physical **XWNV90** is pending. Later PFN accounting and framebuffer-table lifetime remain untested. See [validation](../native-windows-physical-map/validation.json) and [deployment](../native-windows-physical-map/ftp-upload.json).\n\n'
p.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWNV90 pending.')
