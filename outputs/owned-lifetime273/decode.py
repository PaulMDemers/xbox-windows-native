"""Independent terminal decoder. Complete accounting alone does not prove reuse."""
import struct
MAGIC=0x3337324e5758
def decode(data,require_four_binds=True):
    assert 768<=len(data)<=8960 and len(data)%8==0
    h=struct.unpack_from('<16Q',data)
    assert h[:4]==(MAGIC,273,len(data),4) and h[4]<=128
    assert len(data)==768+64*h[4]
    assert h[6:9]==(0,0,0),'Core/gate/transport error union'
    assert h[9] and h[10:13]==(2,0,1),'Unsealed or active observer'
    assert h[13]<=15 and h[14:]==(1,0)
    watches=[];intervals=[];counts=[[0,0] for _ in range(4)]
    def event(e,n=1,last=None):
        seq,identity,generation,kind,slot,code=e
        assert 0<seq<=h[5] and slot<4 and n>0
        assert identity==watches[slot]['identity'] and generation==watches[slot]['generation']
        if kind==2:assert code>>8<4 and code&255 in (1,2);counts[slot][0]+=n
        elif kind in (3,4):
            assert (code>1 if kind==3 else code==1);counts[slot][1]+=n
        else:raise AssertionError('Unknown event kind')
        end=seq+n-1;assert end<=h[5] and (last is None or last==end)
        intervals.append((seq,end,slot,kind))
    reserved=[]
    for i in range(4):
        w=struct.unpack_from('<20Q',data,128+i*160)
        identity,generation,binds,decrements,live,has_bind,has_free,slot=w[:8]
        assert identity and generation and slot==i and live in (0,1) and has_bind in (0,1) and has_free in (0,1)
        assert live==1-has_free and bool(binds)==bool(has_bind)
        assert all(identity!=x['identity'] and generation!=x['generation'] for x in watches)
        watches.append(dict(identity=identity,generation=generation,binds=binds,decrements=decrements,live=live,has_bind=has_bind,has_free=has_free))
        reserved.append((w[8:14],w[14:20]))
    for i,(first,final) in enumerate(reserved):
        if watches[i]['has_bind']:
            assert first[3:5]==(2,i);event(first)
        else:assert first==(0,)*6
        if watches[i]['has_free']:
            assert final[3:5]==(4,i);event(final)
        else:assert final==(0,)*6
    prior_run_end=0
    for i in range(h[4]):
        run=struct.unpack_from('<8Q',data,768+i*64)
        assert run[3] in (2,3) and run[0]>prior_run_end
        event(run[:6],run[7],run[6]);prior_run_end=run[6]
    end=0
    for start,stop,slot,kind in sorted(intervals):
        assert start==end+1,'Dropped or duplicated sequence interval';end=stop
        first,final=reserved[slot]
        if kind==2:assert start>=first[0],'Earlier bind missing from reserved slot'
        if watches[slot]['has_free']:assert stop<=final[0],'Observation after final free'
    assert end==h[5]
    for i,w in enumerate(watches):assert counts[i]==[w['binds'],w['decrements']]
    if require_four_binds:
        assert all(w['has_bind'] for w in watches) and h[13]==15,'Missing actual bind or snapshot'
    return dict(accounting_complete=True,sequence=h[5],runs=h[4],watches=watches,captures=h[13],
        full_reuse_qualified=False,limits='Requires independent snapshots, live guest coverage, identities and sealed owner acknowledgments')
