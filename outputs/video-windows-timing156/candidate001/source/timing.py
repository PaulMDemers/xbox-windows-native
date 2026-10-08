"""Qualified phase summaries and enforceable host isolation evidence."""
import datetime,math,statistics
def stamp(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def isolation(ready,rows,audit):
    assert ready['passed'] and ready['same_guest_payloads'] and ready['same_parent_and_chain']
    ends=[];starts=[]
    for row in rows:
        lease,before,after,launch,start=row
        assert lease['build_held'] and lease['exclusive_xemu_requested'] and lease['finished']
        assert lease['owner_pid']==start['pid']
        assert before['instance_mode']==after['instance_mode']=='exclusive'
        assert before['instance_pid']==after['instance_pid']
        assert all(r['build_conflict'] and r['xemu_conflict'] for r in [before,after])
        times=list(map(stamp,[ready['utc'],start['utc'],lease['started_utc'],before['checked_utc'],launch['launch_requested_utc'],launch['dashboard_return_utc'],after['checked_utc'],lease['finished_utc']]))
        assert times==sorted(times) and launch['dashboard_return'] and launch['offline_observed']
        starts.append(times[1]);ends.append(times[-1])
    assert ends[0]<=starts[1] and max(ends)<=stamp(audit['utc'])
    return True
def aggregate(parsed):
    assert parsed['passed'] and parsed['timing_passed'] and parsed['profile_attribution_passed']
    assert len(parsed['cases'])==45 and parsed['clock']['frequency']>0
    assert all(c['consistent'] for c in parsed['clock']['cross_checks'])
    groups={}
    for case in parsed['cases']:
        assert len(case['phases'])==2
        targets=set()
        for p in case['phases']:
            assert p['quiet'] and p['timing_passed'] and p['loops']>0 and p['qpc_ticks']>0
            value=p['qpc_ticks']*1e6/parsed['clock']['frequency']/p['loops']
            assert math.isfinite(value) and value>0 and abs(value-p['us_per_draw'])<1e-8
            target=p['target'];assert target in ['primary','memory'] and target not in targets;targets.add(target)
            groups.setdefault((case['size'],target),[]).append(dict(index=case['index'],us_per_draw=value,loops=p['loops'],qpc_ticks=p['qpc_ticks'],tick_ms=p['tick_ms']))
    assert set(groups)=={(i,t) for i in range(15) for t in ['primary','memory']}
    result={}
    for key,samples in groups.items():
        assert len(samples)==3 and len({s['index'] for s in samples})==3
        values=[s['us_per_draw'] for s in samples]
        result[key]=dict(samples=samples,median_us=statistics.median(values),minimum_us=min(values),maximum_us=max(values))
    return result
