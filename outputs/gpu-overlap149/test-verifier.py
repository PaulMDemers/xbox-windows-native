"""Reject damaged recorded lifecycles and arena bytes, including untouched padding."""
import copy,json
from pathlib import Path
from verify import verify,read,sha
from oracle import expected,compare,validate_log
k=Path(__file__).resolve().parent;r=read(k/'verification.json');checks=[]
for case in ['control001','candidate001']:
    a=read(k/case/'audit.json');rows=[e for s in r['results'][case]['lifecycle'] for e in s['events']]
    candidate=case.startswith('candidate')
    for name,mutate in [
        ('missing_unread_download',lambda es:es.pop(3)),
        ('wrong_overlap_offset',lambda es:es[5].update(base=es[5]['base']+64)),
        ('wrong_pitch',lambda es:es[6].update(pitch=256)),
        ('wrong_z16_bpp',lambda es:es[20].update(bytes_per_pixel=4)),
        ('wrong_eviction_cause',lambda es:es[8].update(kind='invalidated'))]:
        damaged=copy.deepcopy(rows);mutate(damaged)
        try:verify(damaged,a['surfaces'],candidate)
        except AssertionError:checks.append(case+':'+name)
        else:raise AssertionError('Mutation accepted: '+name)
    for depth in range(2):
        for stage in range(3):
            ref=expected(depth,stage)
            for offset in (0,27000,32767):
                damaged=bytearray(ref);damaged[offset]^=1
                assert not compare(damaged,ref)['matched'];checks.append(f'{case}:{depth}:{stage}:byte{offset}')
    try:validate_log(a['log'].replace('CPU_PATCH 0 25','CPU_PATCH 0 24').encode())
    except AssertionError:checks.append(case+':bad_store_count')
    else:raise AssertionError('Invalid store count accepted')
p=k/'verifier-tests.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,checks=checks,test_sha256=sha(Path(__file__))),indent=2)+'\n')
print(len(checks),'negative evidence checks passed')
