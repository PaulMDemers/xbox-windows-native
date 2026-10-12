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

fixtures = [read(k / 'candidate001' / 'fixture.json')]
rows = {}
audits = []
for case, fixture in zip(['candidate001'], fixtures):
    out = k / case
    run = Path('D:/xwn302/runs') / ('nt5-map302-' + case)
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
                     fixture_sha256=fixture['fixture_sha256'], replacement_files=fixture['replacement_files'])
    audits.append(a)

m=read(k/'candidate001/mapping.json');snapshot=read(k/'candidate001/snapshot.json')
assert m['passed'] and not m['ordinary_qualified']
assert m['snapshot_sha256']==sha(Path('D:/xwn302/capture001/desktop.ram'))
assert m['private_aliases_sha256']==sha(Path('D:/xwn302/capture001/aliases.json'))
assert m['view']['Physical']==55*1024**2 and m['view']['ReservedBytes']==9*1024**2
assert m['physical_memory']['reserved_pages_excluded_from_runs'] and m['physical_memory']['reserved_pages']==2304
assert m['physical_memory']['highest_pfn']<55*1024**2//4096
assert len(m['roots'])==len(m['processes'])==19 and len(m['pins'])==5
assert snapshot['status']=='captured' and not snapshot['guest_memory_writes'] and not snapshot['guest_register_writes'] and snapshot['breakpoints']==0
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_pins=counts,rows=rows,
 scoped_mapping_passed=True,scoped_diagnostic_passed=True,strict_passed=False,ordinary_qualified=False,
 physical_deployment=False,windows_hd_qualified=False,release_qualified=False,all_owned_sessions_closed=True,
 actual_process_roots=19,reserved_pages=2304,in_range_pfn_entries=0,resident_code_pins=5,
 mapping_sha256=sha(k/'candidate001/mapping.json'),limits=m['limits']+' Reserved PFNs are above actual managed PFN high-water, not 2304 individually inspected PFN structs. Ftdisk49 retained.')
dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['source_pins','scoped_mapping_passed','scoped_diagnostic_passed','strict_passed']},indent=2))
