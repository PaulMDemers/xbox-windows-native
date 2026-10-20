"""Independent synthetic arithmetic/stack oracle; no debugger helper imports."""
from collections import Counter,defaultdict

def validate(text,base,size):
    lines=text.splitlines();assert lines and lines[-1]=='END 00000000 0000002d 00000000'
    stacks=defaultdict(list);calls={};finished=set();legacy=[];requests=Counter()
    bp={};arms=[];pending=None;totals=[];probe_values=set();fixture_values=set()
    maxdepth=0;overlap=False;probe_counts=Counter();zero_returns=0
    for line in lines:
        p=line.split();kind=p[0]
        if kind in ('LOAD','PROC','ORD'):
            assert len(p)==5 and pending is None
            tid,ret,module=[int(x,16) for x in p[1:4]]
            name=int(p[4],16) if kind=='ORD' else bytes.fromhex(p[4]).decode('ascii')
            assert tid and base<=ret<base+size and (module==0 if kind=='LOAD' else module!=0)
            pending=(kind,tid,ret,module,name);requests[kind,name]+=1;legacy.append(pending)
        elif kind=='CALL':
            assert len(p)==9
            ident,tid,api,ret,sp,arg0,arg1,target=[int(x,16) for x in p[1:]]
            assert ident==len(calls)+1 and api in (1,2,3) and bp[target]==api
            assert sp and ret and all(0<=v<=0xffffffff for v in [sp,arg0,arg1])
            if api<3:
                assert pending and pending[1:3]==(tid,ret)
                assert (pending[0]=='LOAD')==(api==1)
                assert api==1 or pending[3]==arg0
                if pending[0]=='ORD':assert pending[4]==arg1
            else:
                assert pending is None and arg0<=3 and target in probe_values
                probe_counts[tid]+=1
            expected_sp=sp+4+({1:4,2:8,3:0}[api]);assert expected_sp<=0xffffffff
            if stacks[tid]:assert expected_sp<=calls[stacks[tid][-1]]['sp']
            calls[ident]=dict(tid=tid,api=api,ret=ret,sp=sp,expected_sp=expected_sp,a=arg0,b=arg1,request=pending)
            pending=None;stacks[tid].append(ident)
            maxdepth=max(maxdepth,len(stacks[tid]));overlap|=sum(bool(v) for v in stacks.values())>1
        elif kind=='RETURN':
            assert len(p)==7 and pending is None
            ident,tid,api,ret,sp,value=[int(x,16) for x in p[1:]]
            assert stacks[tid] and stacks[tid][-1]==ident and ident not in finished
            c=calls[ident];assert (tid,api,ret,sp)==(c['tid'],c['api'],c['ret'],c['expected_sp'])
            assert 0<=value<=0xffffffff
            if api==3:
                d,s=c['a'],c['b'];assert value==(((s+d)^0x600abcde)+d*(d+1)//2)&0xffffffff
            else:
                k,_,_,_,n=c['request']
                missing=n in ('xwn600-does-not-exist.dll','missing600',8)
                assert (value==0)==missing
                zero_returns+=value==0
                if n in ('probe600',7):probe_values.add(value)
                if n=='C:\\xwn600-kit\\fixture.dll':fixture_values.add(value)
            finished.add(ident);stacks[tid].pop()
        elif kind=='BP':
            assert len(p)==4
            index,address,api=[int(x,16) for x in p[1:]]
            assert index==len(bp) and address not in bp and api in (0,1,2,3)
            bp[address]=api
        elif kind=='ARM':arms.append(tuple(int(x,16) for x in p[1:]))
        elif kind=='TOTAL':totals.append(tuple(int(x,16) for x in p[1:]))
        elif kind=='STALE':
            tid,address,sp=[int(x,16) for x in p[1:]];assert bp[address]==0
            assert not any(calls[i]['ret']==address for i in stacks[tid])
            if stacks[tid]:assert sp<=calls[stacks[tid][-1]]['expected_sp']
        else:assert kind in ('IMAGE','THREAD','DLL','END'),line
    assert pending is None and len(calls)==len(finished)==45 and not any(stacks.values())
    assert totals==[(45,45,len(bp))] and len(arms)==2 and {a[0] for a in arms}=={0,1}
    assert all(bp[a[2]]==a[0]+1 for a in arms)
    assert sum(x.startswith('END ') for x in lines)==1
    expected=Counter({('LOAD','user32.dll'):1,('LOAD','xwn600-does-not-exist.dll'):1,
        ('LOAD','C:\\xwn600-kit\\fixture.dll'):2,('PROC','MessageBeep'):1,
        ('PROC','probe600'):8,('PROC','missing600'):2,('ORD',7):8,('ORD',8):2})
    assert requests==expected and len(legacy)==25 and len(probe_values)==len(fixture_values)==1
    assert len(probe_counts)==2 and set(probe_counts.values())=={10}
    assert maxdepth==4 and overlap and zero_returns==5
    return dict(passed=True,calls=45,returns=45,api_pairs=25,probe_invocations=20,
        calling_threads=2,max_nested_depth=maxdepth,overlapping_threads=overlap,
        failed_lookup_returns=zero_returns,breakpoint_sites=len(bp),
        scope='Original synthetic NT5 call/return transport and arithmetic only; no game/performance/COM evidence.')
