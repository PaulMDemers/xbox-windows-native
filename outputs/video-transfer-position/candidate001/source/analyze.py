"""Summarize qualified batch costs without attributing them to memcpy alone."""
import datetime
import hashlib
import json
import statistics
from pathlib import Path
from protocol import KINDS, GEOMETRIES, rectangles

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
    for cell, (w,h,kind,x,y) in enumerate(GEOMETRIES):
        rows = [c for c in v['cases'] if c['size'] == cell]
        assert len(rows)==3 and len({c['index']//15 for c in rows})==3
        assert all(c['kind']==KINDS[kind] and c['x']==x and c['y']==y for c in rows)
        geometry=rectangles(rows[0]['index'])
        group=dict(cell=cell,width=w,height=h,kind=KINDS[kind],x=x,y=y,
                   bytes_per_draw=w*h*4,rectangles=len(geometry),
                   row_copies_per_draw=sum(b-t for l,t,r,b in geometry),phases={})
        for target in ['memory','primary']:
            phases=[p for c in rows for p in c['phases'] if p['target']==target]
            assert len(phases)==3 and all(p['timing_passed'] and p['quiet'] for p in phases)
            values=[p['us_per_draw'] for p in phases]
            group['phases'][target]=dict(samples_us=values,median_us=statistics.median(values),
                minimum_us=min(values),maximum_us=max(values),max_over_min=max(values)/min(values))
        groups.append(group)
    contrasts=[]
    for start in [0,3,6]:
        g=groups[start:start+3]
        for target in ['memory','primary']:
            med=[r['phases'][target]['median_us'] for r in g]
            contrasts.append(dict(kind=g[0]['kind'],target=target,
                x128_over_origin=med[1]/med[0],y160_over_origin=med[2]/med[0]))
    sweep=[dict(width=g['width'],**g['phases']) for g in groups[9:]]
    return dict(passed=True, ordinary_emulator_only=True, physical_qualified=False,
        cooperative_exclusive_leases_verified=True, groups=groups, contrasts=contrasts, width_sweep=sweep,
        limits=['Three repetitions in one boot; not independent-boot reproducibility.',
                'GDI rendering/API and upload are timed together; DIB is not an exact upload subtraction.',
                'Translation holds shape/counts constant but moves both buffers; it does not change their relative addresses.',
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
