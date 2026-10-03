from pathlib import Path
import json
kit=Path(__file__).resolve().parent
u=json.loads((kit/'ftp-upload.json').read_text());v=json.loads((kit/'validation.json').read_text())
assert u['completed_utc'] and not u['launched'] and 'error' not in u
assert len(u['files'])==3 and len(u['unchanged_files_verified'])==30
assert all(f['final_name_verified'] and f['staging_readback_equal'] for f in u['files'])
v['installed_on_physical_console']=True;v['uploaded_utc']=u['completed_utc'];v['physical_tested']=False
(kit/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
p=kit/'REPORT.txt';s=p.read_text();marker='Final validation: '
assert marker not in s
s+='\n'+marker+'both display sizes passed; previous HAL and altered kernel\nwere rejected before entry. The final 42-checkpoint trace passed with 22\nforbidden boundaries watched. The MM-prefix memory run contains 15357\npages starting at PFN 3, matching its descriptor filter. The 26-descriptor\nloader list is unchanged by the prefix. All 1388 imports and core executable\nsections pass after entry-byte restoration. Normal builds, the missing-MM\nparent guard and the complete source patch-chain verification passed.\n\nUploaded '+u['completed_utc']+'. All 33 application files verified by readback.\nThree XWNM90 files retained under xwnm90 backup names. The console was not\nremotely launched. Physical XWND90 confirmation remains pending.\n'
p.write_text(s,newline='\n')
hardware=kit.parent/'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md';s=hardware.read_text();needle='2. Record video cable/adapter'
assert s.count(needle)==1
paragraph='The [machine-dependent MM entry candidate](../native-windows-physical-mi/REPORT.txt), patch 0031, runs the original MmInitSystem prefix and halts at MiInitMachineDependent entry before page-table changes. Both display sizes, old-HAL/kernel-contract rejection, core code/import audits and a 42-checkpoint trace pass in xemu. All 33 application files were verified after upload; XWNM90 backups are retained. Physical **XWND90** is pending. Type-26 accounting and survival of low-mapping removal remain next-stage work. See [validation](../native-windows-physical-mi/validation.json) and [deployment](../native-windows-physical-mi/ftp-upload.json).\n\n'
assert paragraph not in s;hardware.write_text(s.replace(needle,paragraph+needle),newline='\n')
print('Deployment recorded; physical XWND90 pending.')
