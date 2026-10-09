"""One authorized candidate launch, with explicit missing-alias preflight pins."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
out = root / 'candidate001'
dest = out / 'alias-preflight.json'
assert not dest.exists() and not (out / 'physical.json').exists()
package = read(root / 'package-review.json')
expected = package['helpers']['replay.exe']
assert sha(root / 'artifacts/gdi-probe.exe') == expected
assert sha(root / 'artifacts/replay.exe') == expected
assert read(root / 'control001/finish-state.json')['status'] == 'collected_restored_audited_closed'
# The frozen controller additionally verifies every ready/source/input/closure
# pin and restored baseline before any mutation. Do not edit that controller.
out.mkdir(exist_ok=False)
dest.write_text(json.dumps(dict(source_sha256=sha(Path(__file__)),
    alias_sha256=expected, pinned_replay_sha256=expected,
    controller_sha256=sha(root / 'physical-controller.py'),
    ready_sha256=sha(root / 'physical-ready.json'),
    control_closure_sha256=sha(root / 'control001/closure.json'),
    persistent_keyboard_unplugged_authorization=True,
    scope='Only candidate206; never launch control again or repeat this wrapper.'), indent=2) + '\n', encoding='utf-8')
subprocess.run([sys.executable, str(root / 'physical-controller.py'),
                'deploy-launch', 'candidate001', '--keyboard-unplugged'], check=True)
