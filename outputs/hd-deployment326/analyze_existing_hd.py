"""Read-only timing summary of the closed watched HD runs; no new performance claim."""
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).with_name('performance-review.json')
assert not OUT.exists()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = ROOT/'outputs/video-text-oracle206/gdi-probe.c'
result = {'new_experiment': False, 'physical_access': False,
          'scope': 'Historical physical 256x128 GDI microbenchmarks, not screen FPS/window drag/full-screen throughput',
          'source': {'path': str(source), 'sha256': sha(source)}, 'runs': {}}
identities = []
for mode, kit, remote in [('720p', 'hd-observed315', 'xwnhd315'),
                          ('1080i', 'hd-physical324', 'xwnhd324')]:
    k = ROOT/'outputs'/kit
    final = read(k/'final-review.json')
    assert final['scoped_passed'] and final['integrity_passed'] and not final['strict_passed']
    package = read(k/'package.json')
    identities.append(next(r['sha256'] for r in package['helpers'] if r['name'] == 'replay.exe'))
    collection = read(k/'physical001/collection.json')['files']
    samples = []
    for index in range(5):
        path = '/F/'+remote+'/sample'+str(index)+'/gdi-baseline.txt'
        local = k/'artifacts/physical001'/path.lstrip('/')
        digest = sha(local)
        assert digest == collection[path]['sha256']
        rows = [line.split() for line in local.read_text().splitlines()]
        assert [r for r in rows if r[0] == 'PASS'] == [['PASS','0','0','0']]
        assert [r for r in rows if r[0] == 'XWN_GDI_PROBE_VERSION'] == [['XWN_GDI_PROBE_VERSION','11','256','128']]
        timing = [list(map(int, r[1:])) for r in rows if r[0] == 'TIMING_kind_count_ms']
        assert len(timing) == 5 and [r[0] for r in timing] == list(range(5))
        assert all(count > 0 and elapsed >= 1500 for _, count, elapsed in timing)
        snapshots = [int(r[3]) for r in rows if r[0] == 'STATS_LATENCY_kind_phase_ms']
        assert len(snapshots) == 10
        window = [list(map(int, r[1:])) for r in rows if r[0] == 'WINDOW_ROUNDS_paints_ms']
        assert len(window) == 1 and window[0][:2] == [40,40]
        samples.append({'path': str(local), 'sha256': digest, 'timing_kind_count_ms': timing,
                        'snapshot_latency_ms': snapshots, 'window_rounds_paints_ms': window[0]})
    labels = ['fill', 'RAM_to_screen', 'screen_to_RAM', 'overlap_down_right', 'overlap_up_left']
    summary = {}
    for kind, name in enumerate(labels):
        rates = [s['timing_kind_count_ms'][kind][1]*1000/s['timing_kind_count_ms'][kind][2] for s in samples]
        summary[name] = {'median_operations_per_second': statistics.median(rates),
                         'min': min(rates), 'max': max(rates)}
    result['runs'][mode] = {'samples': samples, 'summary': summary,
                           'median_snapshot_latency_ms': statistics.median([x for s in samples for x in s['snapshot_latency_ms']]),
                           'median_window_oracle_wall_ms': statistics.median([s['window_rounds_paints_ms'][2] for s in samples]),
                           'strict_passed': False, 'final_review_sha256': sha(k/'final-review.json')}
assert len(set(identities)) == 1
result['same_replay_binary_sha256'] = identities[0]
result['limits'] = ['Five samples within each single boot, not five independent boot replications',
                    'Different resolution/run; not a matched performance intervention',
                    'Timed region fixed256x128 and includes GDI flush/message/visibility handling',
                    'Statistics snapshots are outside timed operation loops',
                    'Window wall time includes exact readback oracle; not FPS',
                    'No native GPU, memory-cache change or bottleneck attribution established']
OUT.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
print(json.dumps({mode: {key: value for key, value in row.items() if key != 'samples'}
                  for mode, row in result['runs'].items()}, indent=2))
