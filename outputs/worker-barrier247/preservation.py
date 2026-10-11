"""Finite parser/preconditions, no state mutation, retry or native ownership."""
import re

def preconditions(t):
    assert t['renderer_valid']==1 and not t['surface_truncated']
    assert t['current_fifo_valid'] and t['wait_mask']==0
    assert not t['current_pg_only'][3], 'Pending PG interrupt'
    f=t['current_fifo'];assert not f[0] and not f[2]
    assert f[4]==f[5]==0 and f[6]==0, 'Not empty zero-address parser'
    c=t['context'];assert not any(c[:8]) and c[16]==1 and c[17]==1
    s=t['surfaces'];assert len(s)==t['surface_count']==3
    assert sum(v[1] for v in s)==3072000
    for i,v in enumerate(s):
        a,n,p,w,h,flags,callback=v[:7]
        assert 0<a<64*1024**2 and 0<n<=16*1024**2 and a+n<=64*1024**2
        assert p*h<=n and w==640 and h==480
        assert flags&3 and not flags&12 and callback==1
        assert all(a+n<=o[0] or o[0]+o[1]<=a for o in s[:i])
    return [[v[0],v[1]] for v in s]

def preserve_tuple(reply):
    items=re.findall(r'(?<![a-z_])([a-z][a-z_]*\d*)=(\d+)',reply)
    keys=['state','tuple_published','publication_version','surfaces','dirty','downloaded','bytes','error','reason','references_retired','native_grant','old_halt','consume_stop','consume_steps','consume_words','wait_before','wait_after']
    keys += [f'{label}{i}' for label in ['request','gate'] for i in range(10)]
    assert len(items)==len(keys) and len(dict(items))==len(keys) and set(dict(items))==set(keys)
    r={a:int(b) for a,b in items}
    assert r['state'] in [3,4,5,6] and r['publication_version']==232
    assert r['tuple_published']==int(r['state'] in [3,4,6])
    assert not r['references_retired'] and not r['native_grant'] and r['old_halt'] in [0,1]
    assert 0<=r['surfaces']<=128 and 0<=r['downloaded']<=r['dirty']<=r['surfaces']
    assert 0<=r['bytes']<=128*16*1024**2
    assert all(0<=r[key]<2**32 for key in keys if key!='bytes')
    if r['state']==5:
        assert not any(r[key] for key in ['surfaces','dirty','downloaded','bytes','error','reason','consume_stop','consume_steps','consume_words','wait_before','wait_after'])
    r['request']=[r.pop(f'request{i}') for i in range(10)]
    r['gate']=[r.pop(f'gate{i}') for i in range(10)]
    return r
