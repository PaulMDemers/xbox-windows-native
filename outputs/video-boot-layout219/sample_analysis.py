"""Fail-closed v9 counters analysis; device-global deltas remain descriptive."""
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
def analyze(log):
    result=dict(probe_passed=False,copy_checks_passed=False,loop_coverage=False,counters_passed=False,
                timed_loops=[],actual_caps=[],actual_modes=[],intervals=[])
    try:
        rows=[line.split() for line in (log or '').splitlines()]
        assert rows and all(len(v)==4 for v in rows)
        assert rows[0]==['XWN_GDI_PROBE_VERSION','12','256','128'] and rows[-1]==['PASS','0','0','0']
        assert not any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in rows)
        numbers=[(v[0],*[int(n) for n in v[1:]]) for v in rows]
        assert all(0<=n<=0xffffffff for v in numbers for n in v[1:])
        result['actual_caps']=[v for v in rows if v[0]=='CAP_index_value']
        result['actual_modes']=[v for v in rows if v[0].startswith('MODE_')]
        timed=[v for v in numbers if v[0]=='TIMING_kind_count_ms'];result['timed_loops']=timed
        assert len(timed)==5 and [v[1] for v in timed]==list(range(5))
        assert all(1<=v[2]<=20000 and 1500<=v[3]<=181000 for v in timed)
        result['loop_coverage']=True
        checks=[v for v in numbers if v[0]=='COPY_stage_pass']
        assert checks==[('COPY_stage_pass',i,1,0) for i in range(4)]
        result['copy_checks_passed']=True
        ids=[v for v in numbers if v[0]=='IDENTITY_index_value']
        assert len(ids)==8 and [v[1] for v in ids]==list(range(8)) and all(v[3]==0 for v in ids)
        d=[v[2] for v in ids];caps={int(v[1]):int(v[2]) for v in result['actual_caps']}
        assert d==[0x44525758,112,caps[8],caps[10],caps[8]*4,32,caps[8]*caps[10]*4,1]
        assert [v for v in numbers if v[0]=='IDENTITY_RESULT']==[('IDENTITY_RESULT',1,0,0)]
        calls=[v for v in numbers if v[0]=='STATS_CALL_kind_phase_result']
        assert calls==[('STATS_CALL_kind_phase_result',kind,phase,1) for kind in range(5) for phase in range(2)]
        latencies=[v for v in numbers if v[0]=='STATS_LATENCY_kind_phase_ms']
        assert len(latencies)==10 and [(v[1],v[2]) for v in latencies]==[(kind,phase) for kind in range(5) for phase in range(2)]
        assert all(v[3]<180000 for v in latencies)
        snap=[]
        for kind in range(5):
            pair=[]
            for phase,label in enumerate(['STATS_BEFORE_kind_index_value','STATS_AFTER_kind_index_value']):
                values=[v for v in numbers if v[0]==label and v[1]==kind]
                assert len(values)==32 and [v[2] for v in values]==list(range(32))
                a=[v[3] for v in values]
                assert a[:2]==[0x53525758,112] and a[19:21]==[0,1] and a[21:]==[0]*11
                assert all(v<0xffffffff for v in a[2:17]),'Saturated counter'
                pair.append(a)
            before,after=pair
            assert all(after[i]>=before[i] for i in range(2,17)),'Nonmonotonic counter'
            b=before[17]+(before[18]<<32);a=after[17]+(after[18]<<32);assert a>=b
            count=timed[kind][2]
            snap.append(dict(kind=kind,operations=count,ms=timed[kind][3],
                hooks={HOOKS[i]:after[2+i]-before[2+i] for i in range(14)},
                uploads=after[16]-before[16],bytes=a-b,bytes_per_operation=(a-b)/count,
                stats_latency_ms=[latencies[kind*2][3],latencies[kind*2+1][3]],coherence_mismatches=[before[19],after[19]]))
        assert sum(v[0].startswith('STATS_BEFORE_') or v[0].startswith('STATS_AFTER_') for v in numbers)==320
        result.update(probe_passed=True,counters_passed=True,identity=d,intervals=snap,
                      limits='Global PDEV counters include background work. Snapshot/log overhead is outside reported loop time; no engine/upload latency separation.')
    except (AssertionError,ValueError,KeyError,IndexError,TypeError) as exc:
        result['error']=repr(exc)
    return result
