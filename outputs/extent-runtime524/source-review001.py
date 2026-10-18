# SPDX-License-Identifier: MIT
"""Exact declared source adaptation and host provenance before fresh preparation."""
import ast,hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;OUT=K/'source-review001.json';assert not OUT.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((K/'source-copy001.json').read_bytes())
for name,row in manifest.items():
    p=Path(row['parent']);assert sha(p)==row['parent_sha256'];expected=p.read_bytes()
    for a,b in row['substitutions']:assert a.encode() in expected;expected=expected.replace(a.encode(),b.encode())
    assert expected==(K/name).read_bytes() and sha(K/name)==row['sha256'],name
    if name.endswith('.py'):ast.parse(expected)
    if name not in ['preflight002.py','host001.py']:
        assert b'C:/xwn517/' not in expected and b'/mnt/c/xwn517/' not in expected and b'C:/xwn522/' not in expected
h=json.loads((K/'host001.json').read_bytes());assert h['passed']
for n,v in h['source_sha256'].items():assert sha(K/n)==v
for n,v in h['retained_capture_pins'].items():assert sha(Path(n))==v
assert (K/'entry_decode.py').read_bytes()==(K.parent/'entry-receipt498/decode.py').read_bytes()
for n in ['protocol003.py','probe.py','waiter.py','contracts.py','kernel_calls.py','indicator_calls.py','trampoline.py']:
    assert (K/n).read_bytes()==(K.parent/'extent-observer522'/n).read_bytes()
for n in ['Run001.ps1','Invoke.ps1','start-owned.ps1']:
    command="$errors=$null; $tokens=$null; [System.Management.Automation.Language.Parser]::ParseFile('"+str((K/n).resolve())+"',[ref]$tokens,[ref]$errors) | Out-Null; if($errors.Count){$errors | Out-String | Write-Output;exit 1}"
    subprocess.run(['pwsh','-NoProfile','-Command',command],check=True,capture_output=True,text=True,timeout=20)
trace=(K/'trace001.py').read_text();assert trace.count('f.sendcmd(')==1 and 'f.sock.settimeout(20)' in trace and '192.168.' not in trace
run=(K/'Run001.ps1').read_text();assert '-Seconds 240' in run and '-Resource xemu' in run and '-ManualCapture' in run
assert '-FtpPort 6246 -MonitorPort 6244 -GdbPort 6245' in run
preflight=(K/'preflight002.py').read_text();assert "capacity['C']-768*1024**2>=20*1024**3" in preflight
assert "for n,h in {**review['frozen_inputs'],**review['files']}.items():assert sha(Path(n))==h" in preflight
assert not Path('C:/xwn524').exists()
r=dict(passed=True,source_files_reconstructed=len(manifest),host001_verified=True,decoder_exact=True,new_preparation_or_execution=False,physical_access=False,source_sha256={p.name:sha(p) for p in K.iterdir() if p.is_file()})
OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(dict(passed=True,reconstructed=len(manifest)))
