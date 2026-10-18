# SPDX-License-Identifier: MIT
"""Rehash closed static evidence and retain actual tool identity/closure."""
import datetime,hashlib,json,subprocess,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;O=K/'final-review.json';assert not O.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((K/'review001.json').read_bytes());assert r['passed'] and not r['runtime_executed'] and not r['new_XBE_saved']
for n,row in {**r['inputs'],**r['private_files']}.items():
    p=Path(n);assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],n
build=json.loads((K.parent/'entry-colocated516/build001.json').read_bytes())
tool=subprocess.check_output(['wsl','-d','Ubuntu','--','sha256sum','/usr/bin/objdump'],text=True,timeout=20).split()[0]
assert tool==build['inputs']['/usr/bin/objdump']
assert Path('C:/xwn519/review001/diagnostic.txt').read_bytes()==Path('C:/xwn516/review001/new-diagnostic.txt').read_bytes()
assert r['known_entry_tail_references']==[] and r['proposed_bytes']==544096 and r['removed_bytes']==992
assert r['negative_byte_mutations']==5488 and len(r['invalid_lengths_rejected'])==6
assert r['live_prefix_exact'] and r['payload_exact'] and r['inherited_TLS_runtime_unknown'] and not r['physical_root_cause_established']
live=subprocess.check_output(['pwsh','-NoProfile','-Command','Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like "xemu*" -or $_.ProcessName -like "qemu*" } | Select-Object Id,ProcessName | ConvertTo-Json -Compress'],text=True,timeout=20).strip();assert not live
q=subprocess.run(['wsl','-d','Ubuntu','--','pgrep','-a','^qemu-system'],capture_output=True,text=True,timeout=20);assert q.returncode==1 and not q.stdout.strip()
files={str(p):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in Path('C:/xwn519').rglob('*') if p.is_file()}
assert len(files)==2 and not any(p.name.endswith(('.xbe','.qcow2')) for p in Path('C:/xwn519').rglob('*'))
result=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='static extent/ref/header and mutation contract only',inputs_rehashed=len(r['inputs']),private_files_rehashed=len(files),files=files,actual_objdump_sha256=tool,actual_disassembly_matches_pinned516=True,closed_sessions=['93375 exit0'],all_owned_processes_closed=True,physical_access=False,new_XBE_saved=False,guest_preparation=False,queued_launch=False,capacity_free_bytes={d:shutil.disk_usage(d+':/').free for d in ['C','E']},review_sha256=sha(K/'review001.json'),source_sha256=sha(Path(__file__)))
O.write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps({n:result[n] for n in ['passed','inputs_rehashed','private_files_rehashed','all_owned_processes_closed']}))
