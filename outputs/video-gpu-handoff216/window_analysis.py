"""Fail closed on real-window pixel lifecycle plus independent global counter packets."""
def window(log, mode):
    r=dict(passed=False,physical_qualified=False)
    try:
        rows=[v.split() for v in (log or '').splitlines()];assert rows and all(len(v)==4 for v in rows)
        n=[(v[0],*[int(x) for x in v[1:]]) for v in rows]
        assert all(0<=x<=0xffffffff for v in n for x in v[1:])
        assert not any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in n)
        assert [v for v in n if v[0]=='WINDOW_CASE_pass']==[('WINDOW_CASE_pass',1,40,0)]
        rounds=[v for v in n if v[0]=='WINDOW_ROUNDS_paints_ms'];assert len(rounds)==1
        _,moves,paints,ms=rounds[0];assert moves==40 and 40<=paints<0xffffffff and 0<ms<180000
        for label in ['WINDOW_STATS_CALL','WINDOW_PROFILE_CALL']:
            assert [v for v in n if v[0]==label]==[(label,i,1,0) for i in range(2)]
        join=lambda a,i:a[i]+(a[i+1]<<32)
        stats=[];profiles=[]
        for phase in range(2):
            packet=[]
            for label in ['WINDOW_STATS_index_value','WINDOW_PROFILE_index_value']:
                vals=[v for v in n if v[0]==label and v[1]==phase]
                assert len(vals)==32 and [v[2] for v in vals]==list(range(32));packet.append([v[3] for v in vals])
            s,p=packet;assert s[:2]==[0x53525758,112] and s[19:21]==[0,1] and s[21:]==[0]*11
            assert all(x<0xffffffff for x in s[2:17]) and join(s,17)<(1<<64)-1
            assert p[:4]==[0x544d5758,113,128,mode] and 0<join(p,4)<1<<63
            assert p[6]==128 and join(p,7)<=join(p,9) and p[11:14]==[0,0,0] and p[27:]==[0]*5
            calls=[p[14+3*i] for i in range(4)];ticks=[join(p,15+3*i) for i in range(4)]
            assert all(x<0xffffffff for x in calls) and all(x<(1<<64)-1 for x in ticks)
            assert p[26]==256+2*sum(calls)*mode
            if not mode:assert ticks==[0]*4
            stats.append(s);profiles.append((p,calls,ticks))
        assert profiles[0][0][4:14]==profiles[1][0][4:14]
        ds=[b-a for a,b in zip(stats[0][2:17],stats[1][2:17])];db=join(stats[1],17)-join(stats[0],17)
        dc=[b-a for a,b in zip(profiles[0][1],profiles[1][1])];dt=[b-a for a,b in zip(profiles[0][2],profiles[1][2])]
        assert all(x>=0 for x in ds+dc+dt) and db>=40*256*128*4
        assert ds[0]+ds[1]>=80 and ds[2]>=40 and ds[14]>=80
        assert dc[0]+dc[1]>=80 and dc[2]>=80 and dc[3]>=80
        if mode:assert dt[0]+dt[1]>0 and dt[2]>0 and dt[3]>0
        f=join(profiles[0][0],4)
        r.update(passed=True,moves=40,exact_readbacks=40,paints=paints,wall_ms=ms,frequency=f,
                 global_hook_deltas=ds[:14],global_uploads=ds[14],global_bytes=db,
                 phase_calls=dc,phase_ticks=dt,phase_ms=[x*1000/f for x in dt],
                 limits='Actual owned-window WM_PAINT/TextOut lifecycle. Wall time includes exact readback oracle; not FPS. Global phases/counts include background; engine covers BitBlt/CopyBits only.')
    except (AssertionError,ValueError,TypeError,IndexError,KeyError) as e:r['error']=repr(e)
    return r
