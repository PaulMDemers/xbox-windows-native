"""Exercise ticket ownership in a disposable directory, never the live queue."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

k = Path(__file__).resolve().parent
out = k / 'artifacts' / 'queue-review001'
dest = k / 'queue-review001.json'
assert not out.exists() and not dest.exists()
out.mkdir(parents=True)
shutil.copyfile(k / 'queue.py', out / 'queue.py')
report = out / 'report.txt'
report.write_text('Disposable protocol review; no physical access.\n', encoding='utf-8')
rows = []

def run(argv, success):
    p = subprocess.run([sys.executable, str(out / 'queue.py'), *argv], capture_output=True, text=True)
    assert (p.returncode == 0) == success, (argv, p.stdout, p.stderr)
    rows.append({'arguments': argv, 'expected_success': success, 'returncode': p.returncode})

run(['claim', 'usb'], False)
run(['claim', 'pci'], False)
run(['claim', 'audio'], True)
run(['claim', 'audio'], False)
run(['close', 'usb', '--report', str(report)], False)
run(['close', 'audio'], False)
run(['close', 'audio', '--report', 'relative.txt'], False)
run(['close', 'audio', '--report', str(report)], True)
run(['claim', 'audio'], False)
run(['claim', 'pci'], False)
run(['claim', 'usb'], True)
run(['close', 'usb', '--report', str(report)], True)
run(['claim', 'pci'], True)
run(['close', 'pci', '--report', str(report)], True)
run(['claim', 'pci'], False)
run(['close', 'pci', '--report', str(report)], False)
state = {p.name: json.loads(p.read_text()) for p in (out / 'state').glob('*.json')}
assert len(state) == 6 and all(state[n + '-closed.json']['baseline_restored'] for n in ('audio', 'usb', 'pci'))
dest.write_text(json.dumps({'passed': True, 'physical_access': False, 'live_state_accessed': False,
                           'checks': rows, 'source_sha256': hashlib.sha256((k / 'queue.py').read_bytes()).hexdigest(),
                           'limits': 'Protocol ownership gates only; restoration is an operator declaration requiring actual evidence.'}, indent=2) + '\n')
print('Sixteen isolated queue ownership checks PASS')
