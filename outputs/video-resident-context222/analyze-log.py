"""Independent exact ordinary workload grammar; no completion inferred from FTP."""
def analyze(data):
    r=dict(passed=False)
    try:
        assert isinstance(data,bytes) and len(data)<65536 and data.endswith(b'\r\n')
        rows=[]
        for line in data.decode('ascii').splitlines():
            p=line.split();assert len(p)==4
            values=[int(v) for v in p[1:]];assert all(0<=v<=0xffffffff for v in values)
            rows.append((p[0],values))
        def one(tag,value):assert [v for label,v in rows if label==tag]==[value]
        one('BEGIN_CPU_OWNER_ONLY',[222,16384,0]);one('INSTALL_BEFORE_WORK',[0,0,0])
        one('OWNER_STALE_SHORT_CLEANUP',[1,1,1]);one('COMPLETE_CPU_OWNER_ONLY',[65,65,65])
        one('VERIFIED_JOINED',[3194880,1,4]);one('INSTALL_BEFORE_RESTART',[0,0,0]);one('NORMAL_RESTART_REQUEST',[222,0,0])
        waits=[v for label,v in rows if label=='WAIT_JOIN'];assert len(waits)==1 and waits[0][1:]==[4,0] and waits[0][0]<4
        leases=[v for label,v in rows if label=='LEASE'];releases=[v for label,v in rows if label=='RELEASE'];workers=[v for label,v in rows if label=='WORKER']
        assert len(leases)==len(releases)==64 and sorted(workers)==[[i,16,0] for i in range(4)]
        assert sorted(v[1] for v in leases)==list(range(2,66))
        assert sorted(v[:2] for v in leases)==sorted(v[:2] for v in releases) and all(v[2]==0 for v in releases)
        for worker in range(4):assert sum(v[0]==worker for v in leases)==16
        assert all(0<=v[0]<4 and 0x100000<=v[2]<=0x03bfc000 and v[2]%4096==0 for v in leases)
        active={};seen=set()
        for tag,v in rows:
            # Release logging follows the actual release; another worker can log
            # its next acquisition first. Log interleaving is not lease overlap.
            if tag=='LEASE':assert v[0] not in active and v[1] not in seen;active[v[0]]=v[1];seen.add(v[1])
            if tag=='RELEASE':assert active.pop(v[0],None)==v[1]
        assert not active
        allowed={'BEGIN_CPU_OWNER_ONLY','INSTALL_BEFORE_WORK','OWNER_STALE_SHORT_CLEANUP','LEASE','RELEASE','WORKER','WAIT_JOIN','COMPLETE_CPU_OWNER_ONLY','VERIFIED_JOINED','INSTALL_BEFORE_RESTART','NORMAL_RESTART_REQUEST'}
        assert all(tag in allowed for tag,v in rows) and rows[-1]==('NORMAL_RESTART_REQUEST',[222,0,0])
        r.update(passed=True,leases=64,allocations=65,releases=65,exposure_refusals=65,verified_bytes=3194880,joined_workers=4,wait_result=waits[0][0])
    except (AssertionError,ValueError,UnicodeError,TypeError) as exc:r['error']=repr(exc)
    return r
