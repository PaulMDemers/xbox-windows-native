"""Independent map-based validation of immutable280 proposed proof rows.
No renderer calls or implicit acceptance of partial/missing evidence.
"""
from collections import defaultdict
LIMIT=67108864
def validate(rows,stage,candidate):
    assert stage in (1,2,3) and type(candidate) is bool
    kinds=defaultdict(list)
    for row in rows:
        assert len(row)==8 and all(type(v) is int and 0<=v<2**64 for v in row)
        kinds[row[0]].append(row)
    def single(kind):
        assert len(kinds[kind])==1
        return kinds[kind][0]
    a=single(64);h=single(69);timing=single(71)
    assert timing[1]==stage and timing[2]>0 and 0<timing[3]<=timing[4]<timing[5] and timing[6:]==[0,0]
    ack={r[1]:r for r in kinds[72]}
    assert len(kinds[72])==2 and set(ack)=={0,1}
    for phase,r in ack.items():
        assert r[2]==stage*2-1+phase and r[3]>0 and r[3]!=timing[2]
        assert timing[3]<=r[4]<=timing[4] and r[5:]==[1,0,0]
    assert ack[0][3]==ack[1][3] and ack[0][4]<=ack[1][4]
    assert a[1]==h[1]==stage and a[2]==h[7]==0
    assert 0<a[3]==a[4]<2**64-1 and a[5:]==[0,0,1]
    assert h[3]==LIMIT and 0<=h[2]<=2**64-1-LIMIT and all(h[i] for i in [4,5,6])
    boundaries={r[1]:r for r in kinds[70]};assert len(kinds[70])==2 and set(boundaries)=={0,1}
    callback_groups=[];surface_groups=[]
    for phase in (0,1):
        c=boundaries[phase];assert c[2:4]==[1,0] and c[5:7]==[1,0] and 0<c[4]==c[7]<=128
        cb=[r for r in kinds[17] if r[1]==phase];detail=[r for r in kinds[65] if r[1]==phase]
        surface=[r for r in kinds[66] if r[1]==phase]
        assert len(cb)==len(detail)==len(surface)==c[4]
        byid={r[2]:r for r in cb};extra={r[2]:r for r in detail};bycallback={r[3]:r for r in surface}
        assert len(byid)==len(extra)==len(bycallback)==c[4] and byid.keys()==extra.keys()==bycallback.keys()
        assert len({r[2] for r in surface})==c[4] and len({r[6] for r in surface})==c[4]
        roles=0
        for identity,r in byid.items():
            assert identity and r[5]==h[4] and r[6]==ack[phase][3] and r[7]==ack[phase][2]
            assert 0<=r[3]<LIMIT and 0<r[4]<=LIMIT-r[3]
            e=extra[identity];assert e[3:6]==[h[6],h[5],h[2]+r[3]] and e[6:]==[0,0]
            s=bycallback[identity];assert s[2] and s[6] and s[4:6]==r[3:5]
            flags=s[7]&255;role=s[7]>>8
            assert flags in (0,1) and role in range(4) and not roles&role;roles|=role
        assert len({r[6] for r in cb})==1
        ordered=sorted((r[4],r[4]+r[5]) for r in surface)
        assert all(x[1]<=y[0] for x,y in zip(ordered,ordered[1:]))
        callback_groups.append({i:(r[3:7],extra[i][3:]) for i,r in byid.items()})
        surface_groups.append({r[2]:r[3:] for r in surface})
    assert set(r[1] for r in kinds[17])==set(r[1] for r in kinds[65])==set(r[1] for r in kinds[66])=={0,1}
    assert callback_groups[0]==callback_groups[1] and surface_groups[0]==surface_groups[1]
    ts={r[1]:r for r in kinds[67]};extra={r[1]:r for r in kinds[68]}
    assert len(kinds[67])==len(kinds[68])==4 and set(ts)==set(extra)==set(range(4))
    assert len({r[2] for r in ts.values()})==len({r[3] for r in ts.values()})==4
    allocations=[]
    surface_names={r[6] for r in kinds[66]}
    for u,t in ts.items():
        assert t[2] and t[3] and t[3] not in surface_names and t[5]==4096 and t[7]==512
        assert 0<=t[4]<=LIMIT-4096 and t[4]%4096==0 and t[6]==t[4]+256
        assert extra[u][2:]==[0,0,1 if candidate and stage==2 else 2,1,0 if candidate and stage==2 else 1,0]
        a,b=t[4],t[4]+4096
        assert all(b<=x or y<=a for x,y in allocations);allocations.append((a,b))
        assert all(b<=r[4] or r[4]+r[5]<=a for r in kinds[66])
    return dict(complete_texture_boundary=True,stage=stage,callbacks=len(callback_groups[0]),
                mutation_clock=single(64)[3],allocations=allocations,
                candidate=candidate,release_authorized=False,native_gpu_grant=False)

def validate_graph(rows,stage,allocations,candidate):
    result=validate(rows,stage,candidate)
    by=defaultdict(list)
    for row in rows:by[row[0]].append(row)
    assert len(allocations)==4
    surfaces={r[1]:r for r in by[1]};captured={r[2]:r for r in by[66] if r[1]==0}
    assert len(surfaces)==len(by[1])==len(captured) and surfaces.keys()==captured.keys()
    for identity,s in surfaces.items():
        assert captured[identity]==[66,0,identity,s[5],s[2],s[3],s[4],s[6]|(s[7]<<8)]
    units={r[1]:r for r in by[3]};assert len(by[3])==4 and set(units)==set(range(4))
    bindings={r[1]:r for r in by[4]};accounts={r[1]:r for r in by[5]}
    assert len(bindings)==len(by[4]) and len(accounts)==len(by[5])
    for t in by[67]:
        u,identity,name,allocation,span,start,length=t[1:]
        released=candidate and stage==2
        assert units[u][2]==(0 if released else identity) and bindings[identity][2:4]==[1 if released else 2,name]
        assert accounts[identity][2:5]==[1 if released else 2,1,0 if released else 1] and allocation==allocations[u]
        cache=[r for r in by[2] if r[2]==identity]
        assert len(cache)==1 and cache[0][3:7]==[start,length,0,0]
        assert units[u][3]==(1 if stage==3 else 0)
    result['full_graph_and_native_allocations_linked']=True
    return result
