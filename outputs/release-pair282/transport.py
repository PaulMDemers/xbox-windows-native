"""Independent fixed-record and three-graph proof decoder. No runtime authority."""
import struct
from collections import Counter
import decode
def read(data):
    assert len(data)>=280 and len(data)%8==0
    records=[list(struct.unpack_from('<16Q',data,i*128)) for i in range(2)]
    groups=[];offset=256
    for stage in range(1,4):
        assert offset+8<=len(data)
        count=struct.unpack_from('<Q',data,offset)[0];offset+=8
        assert 0<count<=180000 and offset+count*64<=len(data)
        rows=[list(r) for r in struct.iter_unpack('<8Q',data[offset:offset+count*64])]
        groups.append(rows);offset+=count*64
    assert offset==len(data)
    return records,groups
def inspect(records,groups,candidate):
    assert type(candidate) is bool and len(records)==2 and len(groups)==3
    for i,r in enumerate(records):
        assert len(r)==16 and all(type(v) is int and 0<=v<2**64 for v in r)
        assert r[:4]==[280,1 if i==0 else 4,int(candidate),3 if i==0 else 5]
        assert r[4:10]==[0,1,15 if candidate else 0,1,i,2 if i==0 else 3]
        assert r[10]>0 and r[11:13]==([3,4] if i==0 else [5,6])
        assert 0<r[14]<=r[15]<=r[13]
    assert records[0][10]==records[1][10] and records[0][13]<records[1][14]
    assert all(r[0] in set(range(1,19))|set(range(30,34))|set(range(50,73)) for g in groups for r in g)
    result=[decode.validate(g,s+1,candidate) for s,g in enumerate(groups)]
    boundaries=[[r for r in g if r[0]==71][0] for g in groups]
    assert all(b[2]==records[0][10] for b in boundaries)
    assert boundaries[0][4]<=boundaries[1][3] and boundaries[1][4]<=boundaries[2][3]
    assert boundaries[1][3]==records[0][14] and boundaries[2][3]==records[1][14]
    keys=[];callbacks=[];surfaces=[]
    for g in groups:
        keys.append(sorted(r for r in g if r[0]==67))
        callbacks.append(sorted((r[1],r[2],*r[3:7]) for r in g if r[0]==17))
        surfaces.append(sorted(r for r in g if r[0]==66))
    assert keys[0]==keys[1]==keys[2]
    assert callbacks[0]==callbacks[1] and surfaces[0]==surfaces[1]
    assert result[0]['mutation_clock']==result[1]['mutation_clock']
    # Exact retained graph comparison: transformations only on a local expected
    # copy, never on observations or evidence supplied to the scalar validator.
    selected={r[2] for r in keys[0]}
    expected=[]
    for row in groups[0]:
        if row[0]==17 or row[0]>=64:continue
        r=row.copy()
        if candidate:
            if r[0]==3:
                assert r[2] in selected and r[3]==0;r[2]=0;r[4]=1
            elif r[0] in (4,5) and r[1] in selected:
                assert r[2]==2;r[2]=1
                if r[0]==5:assert r[3:5]==[1,1];r[4]=0
        expected.append(r)
    assert expected==[r for r in groups[1] if r[0]<64 and r[0]!=17]
    return dict(complete_proposed_transport=True,candidate=candidate,stages=3,
                cpu_epochs=[1,2,3,4,5,6],retained_graph=True,native_gpu_grant=False)
