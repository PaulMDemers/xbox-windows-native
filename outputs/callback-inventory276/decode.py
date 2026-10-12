"""Independent immutable CPU inventory parser; observation is not admission."""
import re
def decode(text):
    h={k:int(v) for k,v in re.findall(r'(?<![\w])(\w+)=(\d+)',text)}
    assert h['version']==276 and h['available']==h['done']==1
    assert h['state']==6 and h['reason']==14 and h['error']==h['cpu_reason']==0
    assert h['stage']==h['epoch']==1 and h['phase']==h['native_grant']==0
    assert h['capacity']==256 and 0<=h['count']<=256
    assert h['thread'] and h['worker'] and h['thread']!=h['worker'] and h['device']
    assert h['started']<=h['when']<=h['finished']<h['deadline']
    entries=re.findall(r'(?<!\w)c(\d+)=([0-9:]+)',text);assert len(entries)==h['count']
    rows=[]
    for n,values in entries:
        assert int(n)==len(rows);r=list(map(int,values.split(':')))
        assert len(r)==7 and all(0<=v<2**64 for v in r)
        identity,start,size,opaque,function,region,absolute=r
        assert identity and function and region and opaque==h['device'] and size>0
        assert start<0x4000000 and start+size<=0x4000000 and absolute>=start
        assert all(identity!=p[0] for p in rows)
        if rows:assert (function,region,absolute-start)==(rows[0][4],rows[0][5],rows[0][6]-rows[0][1])
        rows.append(r)
    return dict(header=h,callbacks=rows,read_only_observation=True,admission_passed=False)
