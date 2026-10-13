"""Independent fixed-width348 packet and actual interval coverage gate."""
def analyze(text,mode):
    result={'passed':False,'mode':mode,'intervals':[]}
    try:
        assert mode in [0,1];lines=[v.split() for v in text.splitlines()]
        packets=[v for v in lines if v and v[0].startswith('PRIMARY348_')]
        assert len(packets)==15*2*33
        pos=0
        times=[v for v in lines if v and v[0]=='LARGE_TIMING']
        assert len(times)==15 and [int(v[1]) for v in times]==list(range(15))
        assert all(len(v)==4 and 0<int(v[2])<=20000 and 750<=int(v[3])<=30000 for v in times)
        loops={int(v[1]):int(v[2]) for v in times}
        for id in range(15):
            pair=[]
            for phase in [0,1]:
                assert packets[pos]==['PRIMARY348_PACKET',str(id),str(phase),'1'];pos+=1;data=[]
                for index in range(32):
                    v=packets[pos];pos+=1
                    assert len(v)==4 and v[:3]==['PRIMARY348_AFTER' if phase else 'PRIMARY348_BEFORE',str(id),str(index)]
                    n=int(v[3]);assert 0<=n<=0xffffffff;data.append(n)
                assert data[:4]==[0x50435758,348,128,mode] and not any(data[11:])
                assert data[4]==data[6]+data[7]+data[8] and data[5]<=data[4] and data[6]+data[7]<=data[5]
                if not mode:assert not any(data[6:8]+data[9:11])
                pair.append(data)
            a,b=pair;assert all(b[i]>=a[i] for i in range(4,9))
            byte_a=a[9]+(a[10]<<32);byte_b=b[9]+(b[10]<<32);assert byte_b>=byte_a
            delta=[b[i]-a[i] for i in range(4,9)];total=byte_b-byte_a
            if id%5 in [2,3]:
                count=loops[id];assert count>0 and delta[1]>=count
                if mode:
                    w,h=[(256,128),(640,360),(960,540)][id//5]
                    assert delta[2]>=count and total>=count*w*h*4
            result['intervals'].append({'id':id,'attempts':delta[0],'eligible':delta[1],'fast':delta[2],'empty':delta[3],'fallback':delta[4],'fast_bytes':total})
        result['passed']=True
    except (AssertionError,ValueError,KeyError,AttributeError,IndexError) as e:result['error']=type(e).__name__
    return result
