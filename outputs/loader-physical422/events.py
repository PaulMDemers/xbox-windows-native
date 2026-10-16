"""Compare actual pre/post event boundaries, preserving record-scan limitations."""
import collections
import hashlib
import json
import subprocess
import sys
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = K / 'events001.json'; assert not out.exists()
activation = read(K / 'activation001.json'); restored = read(K / 'restore001.json')
assert activation['completed'] and restored['completed'] and restored['baseline_restored']
decoder = W / 'outputs/native-windows-physical-f/decode-legacy-events.py'
r = dict(read_only=True, physical_access=False, decoder_sha256=sha(decoder), logs={})
all_new = []
for name, label in [('sysevent.evt', 'system'), ('appevent.evt', 'application')]:
    records = {}; decoded = {}
    for phase, folder, source in [('before', 'activation-before001', activation), ('after', 'after001', restored)]:
        raw = Path('E:/xwn422') / folder / name
        assert sha(raw) == source['captures'][str(raw)]
        target = raw.with_name(label + '-events001.json'); assert not target.exists()
        subprocess.run([sys.executable, '-B', str(decoder), str(raw), '--output', str(target)],
                       check=True, stdout=subprocess.DEVNULL, timeout=30)
        decoded[phase] = dict(path=str(target), sha256=sha(target), raw_sha256=sha(raw))
        records[phase] = read(target)['records']
    before, after = records['before'], records['after']
    boundary = max((x['record'] for x in before), default=0)
    numbers = {phase:collections.Counter(x['record'] for x in rows) for phase, rows in records.items()}
    duplicates = {phase:[n for n,c in counts.items() if c > 1] for phase,counts in numbers.items()}
    fingerprint = lambda row: json.dumps({k:v for k,v in row.items() if k != 'offset'}, sort_keys=True)
    after_set = {fingerprint(x) for x in after}
    preserved = all(fingerprint(x) in after_set for x in before)
    new = [x for x in after if x['record'] > boundary]
    rows = [{k:x[k] for k in ('record', 'generated_unix', 'written_unix', 'source', 'event_id', 'type')} for x in new]
    r['logs'][label] = dict(decoded=decoded, before_records=len(before), after_records=len(after),
        before_boundary=boundary, duplicate_numbers=duplicates, prior_records_preserved=preserved,
        new=rows, boundary_unambiguous=preserved and not any(duplicates.values()))
    all_new.extend(rows)
r['new_warning_error_events'] = [x for x in all_new if x['type'] in (1, 2)]
r['new_eventlog_start_count'] = sum(x['source'] == 'EventLog' and x['event_id'] == 6005 for x in all_new)
r['new_eventlog_shutdown_count'] = sum(x['source'] == 'EventLog' and x['event_id'] == 6006 for x in all_new)
r['all_boundaries_unambiguous'] = all(x['boundary_unambiguous'] for x in r['logs'].values())
r['scanned_delta_warning_error_free'] = r['all_boundaries_unambiguous'] and not r['new_warning_error_events']
r['strict_clean_install_qualified'] = False
r['limitations'] = 'Validated record scan may include inactive-ring records; no message rendering, full disk audit, complete event coverage or fresh-install qualification.'
out.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({k:v for k,v in r.items() if k != 'logs'}, indent=2))
