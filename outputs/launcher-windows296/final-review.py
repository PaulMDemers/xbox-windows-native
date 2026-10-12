"""Read-only paired evidence review after both unique Windows runs are closed."""
import datetime
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
dest = k / 'final-review.json'
assert not dest.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

counts = {}
for name in ['emulator-frozen.json', 'host-frozen.json']:
    pins = read(k / name)
    for path, digest in pins.items():
        p = Path(path)
        if not p.is_absolute():
            p = ws / p
        assert sha(p) == digest, str(p)
    counts[name] = len(pins)

fixtures = [read(k / c / 'fixture.json') for c in ['control001', 'candidate001']]
changed = [n for n in fixtures[0]['files'] if fixtures[0]['files'][n] != fixtures[1]['files'][n]]
assert set(fixtures[0]['files']) == set(fixtures[1]['files'])
assert changed == ['E/Applications/XWNFBoot/default.xbe']
assert fixtures[0]['parent_sha256'] == fixtures[1]['parent_sha256']
rows = {}
audits = []
for case, fixture in zip(['control001', 'candidate001'], fixtures):
    out = k / case
    run = Path('E:/xwn296/runs') / ('nt5-launcher296-' + case)
    a, combined, allocation = [read(out / n) for n in ['audit.json', 'combined-review.json', 'allocation.json']]
    closure = read(out / 'closure.json')
    host = read(run / 'host-exit.json')
    launch = read(out / 'launch.json')
    assert closure['closed'] and closure['never_relaunch_or_recollect']
    assert closure['audit_sha256'] == sha(out / 'audit.json')
    assert closure['cleanup_sha256'] == sha(run / 'cleanup.json')
    assert host['passed'] and host['exit_code'] == 0 and not host['fallback_kill']
    assert len(launch['cycles']) == 1 and launch['cycles'][0]['status'] == 'accepted'
    assert launch['cycles'][0]['dashboard_return']
    assert a['scoped_combined_passed'] and combined['scoped_combined_passed']
    assert not combined['strict_qualification_passed']
    assert not combined['interval_warning_errors']
    assert len(a['warnings_errors']) == 1
    event = a['warnings_errors'][0]
    assert (event['source'], event['event_id'], event['strings']) == ('Ftdisk', 49, ['\\Device\\HarddiskVolume6'])
    assert a['normal_shutdown_count'] == 1 and a['integrity_passed']
    assert len(a['hives']) == 5 and all(v['parsed'] for v in a['hives'])
    assert all(v['matched'] for v in a['files'])
    assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
    assert sha(Path(fixture['fixture_path_windows'])) == fixture['fixture_sha256']
    assert a['audio_capture']['sha256'] == sha(run / 'ac97-output.wav')
    artifacts = {p.relative_to(out).as_posix(): sha(p) for p in sorted((out / 'artifacts').rglob('*')) if p.is_file()}
    (out / 'private-artifacts.json').write_text(json.dumps(artifacts, indent=2) + '\n')
    # Keep host closure evidence beside the compact cold report, without media.
    host_records = {n: dict(sha256=sha(run / n), record=read(run / n))
                    for n in ['cleanup.json', 'host-exit.json', 'host-close.json', 'input-hashes.json']}
    (out / 'host-records.json').write_text(json.dumps(host_records, indent=2) + '\n')
    rows[case] = dict(launch=launch['cycles'][0], scoped_combined_passed=True,
                     strict_qualification_passed=False, warning=event,
                     actual_caps=a['actual_caps'], actual_modes=a['actual_modes'],
                     protected_hash_count=len(a['files']), structural_hives=5,
                     allocation={n: allocation[n] for n in ['directories', 'files', 'directory_clusters', 'orphan_cluster_count', 'errors']},
                     private_artifact_count=len(artifacts), orderly_host_exit=True,
                     fixture_sha256=fixture['fixture_sha256'], launcher_sha256=fixture['launcher_sha256'])
    audits.append(a)
assert audits[0]['actual_caps'] == audits[1]['actual_caps']
assert audits[0]['actual_modes'] == audits[1]['actual_modes']
r = dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         source_pins=counts, fixture_changed_files=changed, rows=rows,
         scope_passed=True, strict_passed=False, physical_deployment=False,
         windows_hd_qualified=False, avpack='composite', framebuffer_reservation_bytes=4194304,
         release_qualified=False, all_owned_sessions_closed=True,
         limits='Ordinary emulator boot/audio/drawing/restart and cold integrity only. '
                'Both retain Ftdisk49. Physical HDTV cable branch and Windows HD timings remain untested by this pair. '
                'No full disk-content equality or hardware performance claim.')
dest.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({n: r[n] for n in ['source_pins', 'fixture_changed_files', 'scope_passed', 'strict_passed', 'windows_hd_qualified']}, indent=2))
