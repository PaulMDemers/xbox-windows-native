"""Close a collected/restored200 comparison once; preserve failures, no console access."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

base = Path(__file__).resolve().parent
workspace = base.parents[1]
case = sys.argv[1]
assert case in ['control001', 'candidate001']
out = base / case
dest = out / 'closure.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
physical = read(out / 'physical.json')
audit = read(out / 'physical-audit.json')
hives = read(out / 'physical-hive-audit.json')
restored = read(out / 'restored-verification.json')
observer = read(out / 'physical-return.json')
ready = read(base / 'physical-ready.json')
assert physical.get('collected_utc') and physical['baseline_restored']
assert not physical['startup_enabled'] and not physical.get('collection_failure')
assert observer['closed'] and restored['passed']
for name, expected in ready['source_pins'].items():
    assert sha(base / name) == expected
for name, expected in ready['input_pins'].items():
    assert sha(workspace / name) == expected
for group in ['before', 'after', 'before_payloads']:
    for row in physical[group].values():
        if row:
            assert sha(workspace / row['path']) == row['sha256']
names = ['physical.json', 'physical-return.json', 'physical-audit.json',
         'physical-hive-audit.json', 'restored-verification.json']
result = dict(closed=True, closed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              case=case, never_relaunch_or_recollect=True, physical_access=False,
              physical_result=True, physical_qualified=False, release_qualified=False,
              scoped_display_passed=audit['scoped_display_passed'] and hives['passed'],
              strict_qualification_passed=False, strict_events_passed=audit['strict_events_passed'],
              boot_warnings_retained=audit['warnings_errors'], baseline_restored=True,
              startup_enabled=False, evidence_pins={name: sha(out / name) for name in names},
              ready_sha256=sha(base / 'physical-ready.json'), source_sha256=sha(Path(__file__)),
              limits='Explicit measurement comparison only; whole-boot strict warnings remain failures.')
dest.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'closed': True, 'scoped_display_passed': result['scoped_display_passed'],
                  'baseline_restored': True, 'strict_qualification_passed': False}))
