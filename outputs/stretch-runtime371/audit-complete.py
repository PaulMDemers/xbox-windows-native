"""Complete an unclosed cold audit with its explicit missing parser dependency.

Windows host wrapper; never launches a guest or edits the frozen auditor.
Existing partial outputs must remain byte-identical. Completed audits refuse.
"""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
case = sys.argv[1]
assert case in ('control001', 'candidate001')
out = k / case
assert not (out / 'audit.json').exists() and not (out / 'closure.json').exists()
assert (Path('C:/xwn371/runs/nt5-stretch371-' + case) / 'cleanup.json').exists()
dest = out / 'audit-completion.json'
assert not dest.exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
save = lambda p, v: p.write_text(json.dumps(v, indent=2) + '\n')
dependency = ws / 'outputs/hd-phase344/large_analysis.py'
pins = {str(p.relative_to(ws)).replace('\\', '/'): sha(p) for p in
        (k / 'audit.py', k / 'audit-complete.py', dependency,
         ws / 'outputs/stretch-probe370/phase_analysis.py')}
existing = {str(p.relative_to(out)).replace('\\', '/'): sha(p)
            for p in out.rglob('*') if p.is_file()}
r = dict(case=case, physical_access=False, guest_relaunched=False,
         utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         supplemental_dependencies=pins, existing_outputs=existing,
         original_failure=('ModuleNotFoundError: No module named large_analysis; '
                           'audit.py line72, phase_analysis.py line2')
                          if case == 'control001' else None,
         status='running', completed=False)
save(dest, r)
root = '/mnt/c/' + str(ws)[3:].replace('\\', '/')
cmd = ['wsl', '-d', 'Ubuntu', '--', 'env',
       'LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu',
       'PYTHONPATH=' + root + '/outputs/hd-phase344',
       'python3', '-B', root + '/outputs/stretch-runtime371/audit.py', case]
proc = subprocess.run(cmd, capture_output=True)
(out / 'audit-completion.stdout.txt').write_bytes(proc.stdout)
(out / 'audit-completion.stderr.txt').write_bytes(proc.stderr)
r['returncode'] = proc.returncode
r['existing_outputs_unchanged'] = all(sha(out / p) == v for p, v in existing.items())
r['supplemental_dependencies_unchanged'] = all(sha(ws / p) == v for p, v in pins.items())
r['completed'] = proc.returncode == 0 and r['existing_outputs_unchanged'] and r['supplemental_dependencies_unchanged'] and (out / 'closure.json').exists()
r['status'] = 'completed' if r['completed'] else 'failed_preserved'
save(dest, r)
print(json.dumps({n:r[n] for n in ('case', 'returncode', 'existing_outputs_unchanged', 'completed')}, indent=2))
if not r['completed']:
    print(proc.stderr.decode(errors='replace'))
    sys.exit(1)
