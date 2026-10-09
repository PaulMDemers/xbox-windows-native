"""Fail closed on113 timer/errors/overflow/coverage; elapsed global body totals."""
def timing(log,expected_mode):
 r=dict(passed=False,intervals=[],mode=expected_mode,physical_qualified=False)
 try:
  rows=[v.split() for v in (log or '').splitlines()];assert all(len(v)==4 for v in rows)
  n=[(v[0],*[int(q) for q in v[1:]]) for v in rows]
  assert [v for v in n if v[0]=='POST_TIMING_kind_pass']==[('POST_TIMING_kind_pass',i,1,0) for i in range(3)]
  assert [v for v in n if v[0]=='PROFILE_CALL_kind_phase_result']==[('PROFILE_CALL_kind_phase_result',kind,phase,1) for kind in range(5) for phase in range(2)]
  packets=[];freq=None;cal=None
  join=lambda a,i:a[i]+(a[i+1]<<32)
  for kind in range(5):
   pair=[]
   for phase,label in enumerate(['PROFILE_BEFORE_kind_index_value','PROFILE_AFTER_kind_index_value']):
    values=[v for v in n if v[0]==label and v[1]==kind]
    assert len(values)==32 and [v[2] for v in values]==list(range(32)) and all(0<=v[3]<=0xffffffff for v in values)
    a=[v[3] for v in values];assert a[:4]==[0x544d5758,113,128,expected_mode]
    f=join(a,4);assert 0<f<(1<<63) and a[6]==128 and join(a,7)<=join(a,9)
    assert a[11:14]==[0,0,0] and a[27:]==[0]*5
    if freq is None:freq=f;cal=a[6:11]
    assert f==freq and a[6:11]==cal
    counts=[a[14+i*3] for i in range(4)];ticks=[join(a,15+i*3) for i in range(4)]
    assert all(c<0xffffffff for c in counts) and all(t<(1<<64)-1 for t in ticks)
    assert a[26]==256+2*sum(counts)*expected_mode
    if not expected_mode:assert ticks==[0]*4
    pair.append((counts,ticks))
   before,after=pair;dc=[a-b for a,b in zip(after[0],before[0])];dt=[a-b for a,b in zip(after[1],before[1])]
   assert all(v>=0 for v in dc+dt) and dc[0]+dc[1]>0
   if expected_mode:assert sum(dt)>0
   r['intervals'].append(dict(kind=kind,body_calls=dc,elapsed_ticks=dt,elapsed_ms=[v*1000/freq for v in dt],
       labels=['EngBitBlt','EngCopyBits','upload_copy_body','complete_upload_wrapper']))
   packets.extend(pair)
  assert sum(v[0].startswith(('PROFILE_BEFORE_','PROFILE_AFTER_')) for v in n)==320
  r.update(passed=True,frequency=freq,calibration_pairs=128,overhead_min_ticks=cal[1]+(cal[2]<<32),
           overhead_max_ticks=cal[3]+(cal[4]<<32),posttiming_pixel_checks=3,
           limits='Global elapsed times include background/preemption; complete wrapper includes nested profiler bookkeeping. OFF/ON comparison measures enabled clock and tick-accounting increment; both retain common bookkeeping. Calibration is direct queries, not complete wrapper overhead.')
 except (AssertionError,ValueError,IndexError,TypeError,KeyError) as exc:r['error']=repr(exc)
 return r
