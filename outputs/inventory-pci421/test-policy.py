"""Compile the actual deployed policy header in a fresh private host capsule."""
import hashlib
import json
import pathlib
import shutil
import subprocess
K = pathlib.Path(__file__).resolve().parent
W = K.parents[1]
out = pathlib.Path('C:/xwn421/host001')
assert not out.exists() and not (K / 'policy-tests001.json').exists()
out.mkdir()
for source in [K / 'policy-test.c', W / 'src/utilities/hardware-report/pci_probe.h']:
    shutil.copy2(source, out / source.name)
command = 'cd /mnt/c/xwn421/host001 && gcc -std=c11 -Wall -Wextra -Werror -g -fsanitize=address,undefined policy-test.c -o policy-test && ./policy-test'
p = subprocess.run(['wsl', '-d', 'Ubuntu', '--', 'bash', '-lc', command], capture_output=True, timeout=60)
(K / 'policy-tests001.log').write_bytes(p.stdout + p.stderr)
r = dict(returncode=p.returncode, command=command, sources={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in out.glob('*') if q.suffix in ('.c', '.h')})
if p.returncode == 0:
    r['result'] = json.loads(p.stdout)
(K / 'policy-tests001.json').write_text(json.dumps(r, indent=2) + '\n')
assert p.returncode == 0, p.stderr
print(json.dumps(r))
