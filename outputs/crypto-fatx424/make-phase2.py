"""Separate consumed-state-safe persistence boot; parent is closed/audited phase1."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
assert not (K/'Invoke003.ps1').exists()
s=(K/'Invoke002.ps1').read_text().replace('E:/xwn424/assembly002/fresh.qcow2','E:/xwn424/runs/nt5-crypto424-emu001/hdd.qcow2').replace('../../assembly002/fresh.qcow2','../nt5-crypto424-emu001/hdd.qcow2')
(K/'Invoke003.ps1').write_text(s,newline='\n')
s=(K/'Run002.ps1').read_text().replace("$PSScriptRoot emu001","$PSScriptRoot emu002").replace('Invoke002.ps1','Invoke003.ps1').replace('-RunId nt5-crypto424-emu001','-RunId nt5-crypto424-emu002')
anchor="if($f.status -ne 'assembled-readback-verified'){throw 'Assembly not verified'}"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
$prior=Get-Content (Join-Path $PSScriptRoot emu001/audit.json) -Raw | ConvertFrom-Json
if(-not $prior.probe.complete -or $prior.normal_shutdown_delta -ne 1 -or -not $prior.host_exit.passed -or -not $prior.allocation.allocation_consistent -or -not $prior.protected_os_exact -or -not $prior.source_unchanged){throw 'Phase1 incomplete or unsafe to continue'}
foreach($h in $prior.hives){if(-not $h.header_valid -or -not $h.clean -or -not $h.independent_raw_values_agree){throw 'Phase1 hive failed'}}
$f.fixture_path_windows='E:/xwn424/runs/nt5-crypto424-emu001/hdd.qcow2'
$f.fixture_sha256=$prior.disk_sha256
''')
(K/'Run003.ps1').write_text(s,newline='\n')
for before,after in [('supervise001.py','supervise002.py'),('logon-owned001.py','logon-owned002.py'),('type-witness001.py','type-witness002.py')]:
 s=(K/before).read_text().replace('emu001','emu002')
 if before=='type-witness001.py':s=s.replace('create.exe','reopen.exe')
 (K/after).write_text(s,newline='\n')
s=(K/'freeze001.py').read_text().replace("out=K/'emu001'","out=K/'emu002'")
(K/'freeze002.py').write_text(s,newline='\n')
print('Distinct phase2 host scripts prepared; no launch.')
