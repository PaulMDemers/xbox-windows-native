from pathlib import Path
import json

kit = Path(__file__).resolve().parent
root = kit.parent.parent
u = json.loads((kit / 'ftp-upload.json').read_text())
v = json.loads((kit / 'validation.json').read_text())
assert u['completed_utc'] and not u['launched'] and 'error' not in u
assert len(u['files']) == 3 and len(u['unchanged_files_verified']) == 30
assert all(f['final_name_verified'] and f['staging_readback_equal'] for f in u['files'])
v.update(installed_on_physical_console=True, uploaded_utc=u['completed_utc'], physical_tested=False)
(kit / 'validation.json').write_text(json.dumps(v, indent=2) + '\n')
p = kit / 'REPORT.txt'
s = p.read_text()
assert 'Uploaded ' not in s
s += ('\nUploaded ' + u['completed_utc'] + '. All 33 files verified by readback.\n'
      'Three physical-tested XWNV90 files retained under xwnv90 backup names.\n'
      'The console was not remotely launched. Physical XWNS90 is pending.\n')
p.write_text(s, newline='\n')
p = root / 'README.md'
s = p.read_text()
needle = 'See [hardware status]'
assert s.count(needle) == 1
s = s.replace(needle,
    'The next candidate **XWNS90** completes the native RAM descriptor scan\n'
    'and checks its counts and candidate spans before MM allocation or PFN setup.\n'
    'Both display modes and a 45-checkpoint trace pass in xemu; it is uploaded\n'
    'with physical testing pending. See the [RAM scan report](outputs/native-windows-physical-scan/REPORT.txt).\n\n' + needle)
s = s.replace('[latest diagnostic](outputs/native-windows-physical-map/REPORT.txt)',
              '[latest diagnostic](outputs/native-windows-physical-scan/REPORT.txt)')
s = s.replace('[patch-check-0032.json](outputs/native-windows-physical-map/patch-check-0032.json)',
              '[patch-check-0033.json](outputs/native-windows-physical-scan/patch-check-0033.json)')
p.write_text(s, newline='\n')
p = kit.parent / 'native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md'
s = p.read_text()
needle = '2. Record video cable/adapter'
assert s.count(needle) == 1
paragraph = ('The [RAM scan candidate](../native-windows-physical-scan/REPORT.txt), patch 0033, '
    'executes the native RAM descriptor scan and checks totals and candidate spans before MM '
    'allocation or PFN setup. Both display modes, rejection tests, code/import audits and a '
    '45-checkpoint trace pass in xemu. The observed two-page accounting difference equals the '
    'BIOS-reserved pages; later PFN handling remains untested. All 33 files were verified after '
    'upload; XWNV90 backups are retained. Physical **XWNS90** is pending. See '
    '[validation](../native-windows-physical-scan/validation.json) and '
    '[deployment](../native-windows-physical-scan/ftp-upload.json).\n\n')
p.write_text(s.replace(needle, paragraph + needle), newline='\n')
print('Deployment recorded; physical XWNS90 pending.')
