"""Review closed ordinary observations from preserved raw packets; never launch or collect."""
import hashlib
import json
import statistics
from pathlib import Path
from sample_analysis import analyze
from dib_analysis import analyze as rows
from timing_analysis import timing
from window_analysis import window

k = Path(__file__).resolve().parent
ws = k.parents[1]
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
dest = k / 'evidence-review.json'
assert not dest.exists()
r = dict(passed=False, physical_access=False, debugger=False, cases=[],
         ordinary_qualified=False, physical_qualified=False, performance_qualified=False)
for mode, case in enumerate(['control001', 'candidate001']):
    out = k / case
    a, c = [read(out / name) for name in ['audit.json', 'closure.json']]
    assert c['closed'] and c['never_relaunch_or_recollect']
    assert c['audit_sha256'] == sha(out / 'audit.json')
    assert c['cleanup_sha256'] == sha(ws / ('work/runs/nt5-phase199-' + case + '/cleanup.json'))
    assert c['source_snapshot_exact'] and c['package_bound'] and c['source_pins_checked'] == 95
    assert not c['physical_access'] and not c['debugger']
    assert a['workload_passed'] and a['integrity_passed']
    assert a['setupapi_unchanged'] and a['event_history_preserved'] and a['startup_unchanged']
    assert len(a['hives']) == 5 and all(v['parsed'] for v in a['hives'])
    assert all(v['matched'] for v in a['files'])
    assert a['normal_shutdown_count'] == 1 and a['dashboard_return']
    assert not a['strict_events_passed'] and not a['strict_qualification_passed']
    assert not a['new_events']['application'] and len(a['warnings_errors']) == 1
    e = a['warnings_errors'][0]
    assert (e['source'], e['event_id'], e['type'], e['strings'], e['data_hex']) == (
        'Ftdisk', 49, 1, ['\\Device\\HarddiskVolume6'],
        '000000000100560000000000310004c0030000000000000000000000000000000000000000000000')
    allocation = read(out / 'allocation.json')
    assert allocation['capture_complete'] and allocation['allocation_consistent']
    assert not allocation['errors'] and allocation['orphan_cluster_count'] == 0
    assert [allocation[n] for n in ['directories', 'files', 'directory_clusters']] == [334, 6739, 335]
    raw = []
    phases, windows, loops = [], [], []
    for i in range(5):
        p = out / ('artifacts/sample%d/gdi-baseline.txt' % i)
        text = p.read_bytes().decode('ascii')
        assert text == a['sample%d/gdi-baseline.txt' % i]
        s, d, t, w = analyze(text), rows(text, 0), timing(text, mode), window(text, mode)
        assert s == a['samples'][i] and d == a['dib_samples'][i]
        assert t == a['phase_samples'][i] and w == a['window_samples'][i]
        assert s['probe_passed'] and d['passed'] and t['passed'] and w['passed']
        assert w['moves'] == w['exact_readbacks'] == w['paints'] == 40
        assert t['frequency'] == w['frequency'] == 1125000
        # Count actual passed labels rather than trusting inherited closure labels.
        n = [v.split() for v in text.splitlines()]
        assert len([v for v in n if v[0] == 'COPY_stage_pass']) == 4
        assert len([v for v in n if v[0] == 'POST_TIMING_kind_pass']) == 3
        raw.append(dict(path=p.relative_to(ws).as_posix(), sha256=sha(p)))
        phases.append(t); windows.append(w); loops.append(s['timed_loops'])
    r['cases'].append(dict(case=case, profile_mode=mode, raw_pins=raw,
        audit_sha256=sha(out/'audit.json'), closure_sha256=sha(out/'closure.json'),
        functional_integrity_passed=True, strict_qualification_passed=False,
        exact_pixel_comparisons=265, original_checks=65, actual_window_readbacks=200,
        timed_loops=25, scanout_comparisons=50, normal_shutdown_count=1,
        allocation=dict(directories=334, files=6739, directory_clusters=335, errors=0, orphans=0),
        window_samples=windows, phase_samples=phases, timed_samples=loops,
        strict_failure=e, calibration_min_ticks=phases[0]['overhead_min_ticks'],
        calibration_max_ticks=phases[0]['overhead_max_ticks']))
summary = lambda x: dict(values=x, median=statistics.median(x), minimum=min(x), maximum=max(x))
r['candidate_phase_ms_per_loop_operation'] = []
for kind in range(5):
    candidate = r['cases'][1]
    values = [[candidate['phase_samples'][i]['intervals'][kind]['elapsed_ms'][bucket] /
               candidate['timed_samples'][i][kind][2] for i in range(5)] for bucket in range(4)]
    r['candidate_phase_ms_per_loop_operation'].append(dict(kind=kind,
        phases={label: summary(v) for label, v in zip(
            ['EngBitBlt', 'EngCopyBits', 'upload_copy_body', 'complete_upload_wrapper'], values)}))
r['candidate_window_phase_ms'] = {label: summary([v['phase_ms'][i] for v in r['cases'][1]['window_samples']])
    for i, label in enumerate(['EngBitBlt', 'EngCopyBits', 'upload_copy_body', 'complete_upload_wrapper'])}
r['window_wall_ms'] = {v['case']: summary([w['wall_ms'] for w in v['window_samples']]) for v in r['cases']}
r.update(passed=True, all_owned_sessions_closed=True,
    limits='Two ordinary fixed-order emulator boots, five within-boot samples each. Functional and cold checks passed; inherited Ftdisk49 remains strict failure. OFF retains calibration/common accounting; ON adds clocks/tick arithmetic. Global, separately acquired stats/phase snapshots include background and may differ at their boundaries. TextOut engine time is unmeasured. Wrapper nests body/bookkeeping; do not add wrapper and body or subtract calibration. Wall time includes readback/oracle. No physical bus, FPS, release or optimization claim.')
dest.write_text(json.dumps(r, indent=2) + '\n', encoding='utf-8')
print('Both closed ordinary observations reviewed: 265 exact pixels each; strict FALSE sole Ftdisk49')
