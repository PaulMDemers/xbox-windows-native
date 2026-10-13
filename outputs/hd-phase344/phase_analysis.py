"""Independent113 packet decoder for exact344/327 large-area intervals; no gate waiver."""
from large_analysis import analyze as large
def analyze(log,mode):
    r=dict(passed=False,physical_qualified=False)
    try:
        assert type(mode) is int and mode in (0,1)
        base=large(log);assert base['passed'],base.get('error')
        rows=[v.split() for v in log.splitlines()];phase=[]
        for at,v in enumerate(rows):
            if v[0].startswith('PHASE344'):
                assert len(v)==4 and all(q.isascii() and q.isdecimal() and int(q)<=0xffffffff for q in v[1:])
                phase.append((at,v[0],*[int(q) for q in v[1:]]))
        assert phase[0][1:]==('PHASE344_VERSION',344,15,2) and phase[-1][1:]==('PHASE344_COMPLETE',15,30,0)
        assert len(phase)==2+15*66
        j=1;previous=None;header=None;intervals=[]
        join=lambda a,i:a[i]+(a[i+1]<<32)
        for ident,case in enumerate(base['cases']):
            pair=[];begin=j
            for side in (0,1):
                assert phase[j][1:]==('PHASE344_PACKET',ident,side,1);j+=1
                a=[]
                for index in range(32):
                    v=phase[j];j+=1
                    assert v[1:4]==('PHASE344_AFTER' if side else 'PHASE344_BEFORE',ident,index)
                    a.append(v[4])
                assert a[:4]==[0x544d5758,113,128,mode] and 0<join(a,4)<1<<63
                assert a[6]==128 and join(a,7)<=join(a,9) and a[11:14]==[0,0,0] and a[27:]==[0]*5
                if header is None:header=a[:14]
                assert a[:14]==header
                counts=[a[14+3*i] for i in range(4)];ticks=[join(a,15+3*i) for i in range(4)]
                assert all(c<0xffffffff for c in counts) and all(t<(1<<64)-1 for t in ticks)
                assert a[26]==256+2*sum(counts)*mode and a[26]<0xffffffff
                if mode==0:assert ticks==[0]*4
                if previous:assert all(x>=y for x,y in zip(counts+ticks,previous))
                previous=counts+ticks;pair.append((counts,ticks))
            # Published together after timer and before existing timing record; no split/relocation accepted.
            positions=[p[0] for p in phase[begin:j]];assert positions==list(range(positions[0],positions[0]+66))
            assert rows[positions[-1]+1][:2]==['LARGE_TIMING',str(ident)]
            dc=[x-y for x,y in zip(pair[1][0],pair[0][0])];dt=[x-y for x,y in zip(pair[1][1],pair[0][1])]
            assert sum(dc[:2])>=case['operations'] and min(dc[2:])>=case['operations']
            if mode:assert sum(dt[:2])>0 and min(dt[2:])>0
            intervals.append(dict(id=ident,kind=case['kind'],size=case['size'],operations=case['operations'],calls=dc,ticks=dt,elapsed_ms=[x*1000/join(header,4) for x in dt],wall_ms=case['elapsed_ms']))
        assert phase[-1][0]>max(i for i,v in enumerate(rows) if v[0]=='LARGE_COMPLETE')
        r.update(passed=True,mode=mode,frequency=join(header,4),intervals=intervals,limits='Device-global elapsed totals include background/preemption. Engine includes BitBlt/CopyBits only; wrapper contains copy body and profiler bookkeeping. Do not sum overlapping categories or infer FPS/speedup. OFF/ON needs a matched driver pair and unchanged original runtime/event/integrity gates.')
    except (AssertionError,ValueError,KeyError,IndexError,TypeError) as exc:r['error']=str(exc)
    return r
