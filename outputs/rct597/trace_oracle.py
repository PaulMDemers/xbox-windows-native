"""Independent expected request multiset, excluding non-subject caller addresses."""
from collections import Counter,defaultdict

def validate(text,base,size):
    rows=[];arms=[];end=[];other=[]
    for line in text.splitlines():
        p=line.split();assert p,line
        if p[0] in ('LOAD','PROC','ORD'):
            assert len(p)==5,line
            tid,ret,arg=map(lambda s:int(s,16),p[1:4])
            name=int(p[4],16) if p[0]=='ORD' else bytes.fromhex(p[4]).decode('ascii')
            assert tid and 0<=arg<=0xffffffff
            row=(p[0],tid,ret,arg,name)
            (rows if base<=ret<base+size else other).append(row)
        elif p[0]=='ARM':arms.append(tuple(int(x,16) for x in p[1:]))
        elif p[0]=='END':end.append(tuple(int(x,16) for x in p[1:]))
        else:assert p[0] in ('IMAGE','THREAD','DLL'),line
    assert len(arms)==2 and sorted(a[0] for a in arms)==[0,1]
    assert len(end)==1 and end[0][0]==0 and end[0][2]==0
    assert end[0][1]==len(rows)+len(other)
    expected=Counter({('LOAD','user32.dll'):1,('LOAD','xwn597-does-not-exist.dll'):1,
                      ('LOAD','C:\\xwn597-kit\\fixture.dll'):2,('PROC','MessageBeep'):1,
                      ('PROC','probe597'):8,('PROC','missing597'):2,('ORD',7):8,('ORD',8):2})
    assert Counter((r[0],r[4]) for r in rows)==expected
    threads=defaultdict(Counter)
    for kind,tid,ret,arg,name in rows:
        threads[tid][kind,name]+=1
        assert (arg==0 if kind=='LOAD' else arg!=0)
    worker=Counter({('LOAD','C:\\xwn597-kit\\fixture.dll'):1,('PROC','probe597'):4,('PROC','missing597'):1,('ORD',7):4,('ORD',8):1})
    assert len(threads)==2 and all(not (worker-counts) for counts in threads.values())
    return dict(passed=True,subject_requests=len(rows),other_requests=len(other),calling_threads=len(threads),scope='API entry requests only; no resolution return, rendering method, or performance inference.')
