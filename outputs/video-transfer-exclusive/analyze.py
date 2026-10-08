"""Summarize qualified batch costs without attributing them to memcpy alone."""
import datetime
import hashlib
import json
import statistics
from pathlib import Path
from protocol import KINDS, SIZES, rectangles

k = Path(__file__).resolve().parent
case = k / 'candidate001'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
utc = lambda s: datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))

def summarize(v, lease, check, closure, launch):
    assert v['ordinary_qualified'] and v['timing_qualified']
    assert lease['build_held'] and lease['exclusive_xemu_requested'] and lease['finished']
    assert check['build_conflict'] and check['xemu_conflict']
    assert check['instance_mode'] == closure['instance']['mode'] == 'exclusive'
    assert check['instance_pid'] == closure['instance']['processId']
    cycle, = launch['cycles']
    assert cycle['status'] == 'accepted' and cycle['dashboard_return']
    assert utc(lease['started_utc']) <= utc(check['checked_utc']) < utc(cycle['launch_requested_utc']) < utc(cycle['dashboard_return_utc']) <= utc(closure['cleanup']['completedUtc']) <= utc(lease['finished_utc'])
    groups = []
    for size, (w, h) in enumerate(SIZES):
        for kind in KINDS:
            rows = [c for c in v['cases'] if c['size'] == size and c['kind'] == kind]
            assert len(rows) == 3 and len({c['index'] // 15 for c in rows}) == 3
            geometry = rectangles(rows[0]['index'])
            group = dict(size=size, width=w, height=h, kind=kind,
                         bytes_per_draw=w*h*4, rectangles=len(geometry),
                         row_copies_per_draw=sum(b-t for l,t,r,b in geometry),
                         bounding_width=max(r for l,t,r,b in geometry),
                         bounding_height=max(b for l,t,r,b in geometry), phases={})
            for target in ['memory', 'primary']:
                phases = [p for c in rows for p in c['phases'] if p['target'] == target]
                assert len(phases) == 3 and all(p['timing_passed'] and p['quiet'] for p in phases)
                values = [p['us_per_draw'] for p in phases]
                group['phases'][target] = dict(samples_us=values, median_us=statistics.median(values),
                    minimum_us=min(values), maximum_us=max(values), max_over_min=max(values)/min(values))
            groups.append(group)
    contrasts = []
    for size in range(3):
        g = {r['kind']: r for r in groups if r['size'] == size}
        med = lambda kind: g[kind]['phases']['primary']['median_us']
        contrasts.append(dict(size=size,
            horizontal16_over_solid=med('horizontal16')/med('solid'),
            vertical16_over_horizontal16=med('vertical16')/med('horizontal16'),
            horizontal16_over_horizontal4=med('horizontal16')/med('horizontal4')))
    return dict(passed=True, ordinary_emulator_only=True, physical_qualified=False,
        cooperative_exclusive_leases_verified=True, groups=groups, contrasts=contrasts,
        limits=['Three repetitions in one boot; not independent-boot reproducibility.',
                'GDI rendering/API and upload are timed together; DIB is not an exact upload subtraction.',
                'Equal area and upload counts do not hold bounding extent or touched addresses constant.',
                'Exclusive cooperative leases do not exclude unrelated host load.',
                'No physical FPS or pure copy bandwidth claim.'])

if __name__ == '__main__':
    names = ['verification.json', 'performance-lease.json', 'lease-check.json', 'closure.json', 'launch.json']
    result = summarize(*(read(case/n) for n in names))
    result['pins'] = {n: sha(case/n) for n in names}
    result['analysis_source_sha256'] = sha(Path(__file__))
    destination = k/'analysis.json'
    assert not destination.exists()
    destination.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result['contrasts'], indent=2))
