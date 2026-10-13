"""Independent actual-dispatch and byte/pixel-report decoder."""
def analyze(text):
    rows=[s.split() for s in (text or '').splitlines() if s.startswith('STRETCH_')]
    def take(tag, ident=None):
        chosen=[r for r in rows if r[0]==tag and (ident is None or r[1]==str(ident))]
        if len(chosen)!=1:raise ValueError('missing/duplicate '+tag+' '+str(ident))
        return list(map(int,chosen[0][1:]))
    try:
        assert take('STRETCH_VERSION')==[370,12,16]
        assert take('STRETCH_COMPLETE')==[12,192,0]
        assert not any(s.startswith('FAIL_STRETCH') for s in (text or '').splitlines())
        result=[]
        for case in range(12):
            packets=[]
            for label in ['STRETCH_BEFORE','STRETCH_AFTER']:
                rr=[r for r in rows if r[0]==label and r[1]==str(case)]
                assert len(rr)==32 and [int(r[2]) for r in rr]==list(range(32))
                v=[int(r[3]) for r in rr];assert all(0<=x<=0xffffffff for x in v)
                assert v[:2]==[0x53525758,112] and v[19:]==[0,1]+[0]*11
                packets.append(v)
            a,b=packets
            timing=take('STRETCH_TIMING',case);assert timing[:2]==[case,16] and 0<=timing[2]<=30000
            dispatch=take('STRETCH_DISPATCH',case)
            assert b[10]>=a[10] and b[11]>=a[11]
            assert dispatch==[case,b[10]-a[10],b[11]-a[11]] and sum(dispatch[1:])>=16
            assert b[16]>=a[16]
            delta=(b[17]+(b[18]<<32))-(a[17]+(a[18]<<32));assert delta>0
            byte=take('STRETCH_BYTES',case);assert byte==[case,delta&0xffffffff,delta>>32]
            assert take('STRETCH_CASE_PASS',case)==[case,32768,int(case%4==0)]
            result.append(dict(case=case,mirrored=case%4!=0,clip_kind=case//4,
                calls=dispatch[1:],uploads=b[16]-a[16],bytes=delta,milliseconds=timing[2],
                independent_positive_oracle=case%4==0,dib_reference_and_source_guards=True))
        assert len(rows)==2+12*(64+4)
        return dict(passed=True,cases=result,limits='Mirrored pixels use independent driver-free GDI DIB reference, not independent rasterizer. Timings are uncalibrated workload elapsed milliseconds; no physical speed claim.')
    except (ValueError,AssertionError,IndexError):
        return dict(passed=False,error='incomplete or inconsistent stretch370 evidence')
