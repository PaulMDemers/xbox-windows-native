"""Fail-closed114 coverage and six independent live pixel cases."""
def analyze(log,enabled):
 r=dict(passed=False,enabled=enabled,cases=[],intervals=[],limits='Device-global counters may include background work; exact pixels and minimum coverage are required, never attributed exclusively to probe.')
 try:
  rows=[v.split() for v in (log or '').splitlines()];n=[(v[0],*[int(x) for x in v[1:]]) for v in rows]
  assert [v for v in n if v[0]=='DIB_CASE_stage_pass']==[('DIB_CASE_stage_pass',i,1,0) for i in range(6)]
  tags=list(range(10,16))+list(range(5))
  assert [v for v in n if v[0]=='DIB_CALL_tag_phase_result']==[('DIB_CALL_tag_phase_result',tag,phase,1) for tag in tags for phase in range(2)]
  timed={v[1]:v[2] for v in n if v[0]=='TIMING_kind_count_ms'}
  for tag in tags:
   pair=[]
   for label in ['DIB_BEFORE_tag_index_value','DIB_AFTER_tag_index_value']:
    vals=[v for v in n if v[0]==label and v[1]==tag]
    assert len(vals)==32 and [v[2] for v in vals]==list(range(32))
    a=[v[3] for v in vals];assert a[:4]==[0x42445758,114,128,enabled] and a[14:]==[0]*18
    assert all(x<0xffffffff for x in a[4:12]),'Counter saturated'
    assert a[4]==sum(a[5:12]),'Attempt accounting mismatch'
    pair.append(a)
   before,after=pair;assert all(after[i]>=before[i] for i in range(4,12))
   delta=[after[i]-before[i] for i in range(4,12)];b=before[12]+(before[13]<<32);a=after[12]+(after[13]<<32);assert b<=a<0xffffffffffffffff
   row=dict(tag=tag,attempts=delta[0],hits=delta[1],empty=delta[2],disabled=delta[3],format=delta[4],clip=delta[5],geometry=delta[6],alias=delta[7],bytes=a-b)
   if not enabled:assert row['hits']==0 and row['bytes']==0 and row['attempts']==row['disabled']
   elif tag in [10,11]:assert row['hits']>=1 and row['bytes']>0
   elif tag==1:assert row['hits']>=timed[1]>0 and row['bytes']>=timed[1]*256*128*4
   (r['cases'] if tag>=10 else r['intervals']).append(row)
  if enabled:
   assert sum(v['clip'] for v in r['cases'] if v['tag'] in [12,13])>0,'Complex fallback not covered'
   assert r['cases'][4]['format']>0,'24bit fallback not covered'
  assert sum(v[0].startswith(('DIB_BEFORE_','DIB_AFTER_')) for v in n)==704
  r['passed']=True
 except (AssertionError,ValueError,IndexError,TypeError,KeyError) as e:r['error']=repr(e)
 return r
