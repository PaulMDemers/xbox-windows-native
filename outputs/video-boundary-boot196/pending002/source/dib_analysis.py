"""Fail-closed115 row coverage plus independent live RGB cases/posttiming."""
def analyze(log,enabled):
 r=dict(passed=False,enabled=enabled,cases=[],intervals=[],limits='Global upload accounting, not exclusive attribution; same instrumentation in both builds.')
 try:
  rows=[v.split() for v in (log or '').splitlines()];n=[(v[0],*[int(x) for x in v[1:]]) for v in rows]
  assert [v for v in n if v[0]=='DIB_CASE_stage_pass']==[('DIB_CASE_stage_pass',i,1,0) for i in range(6)]
  assert [v for v in n if v[0]=='POST_TIMING_kind_pass']==[('POST_TIMING_kind_pass',i,1,0) for i in range(3)]
  tags=list(range(10,16))+list(range(5));timed={v[1]:v[2] for v in n if v[0]=='TIMING_kind_count_ms'}
  assert [v for v in n if v[0]=='DIB_CALL_tag_phase_result']==[('DIB_CALL_tag_phase_result',tag,phase,1) for tag in tags for phase in range(2)]
  for tag in tags:
   pair=[]
   for label in ['DIB_BEFORE_tag_index_value','DIB_AFTER_tag_index_value']:
    vals=[v for v in n if v[0]==label and v[1]==tag];assert len(vals)==32 and [v[2] for v in vals]==list(range(32))
    a=[v[3] for v in vals];assert a[:4]==[0x57525758,115,128,enabled] and a[11:]==[0]*21
    assert all(x<0xffffffff for x in a[4:7]);pair.append(a)
   before,after=pair;assert all(after[i]>=before[i] for i in range(4,7))
   total=lambda a:a[7]+(a[8]<<32);fast=lambda a:a[9]+(a[10]<<32)
   assert total(before)<=total(after)<0xffffffffffffffff and fast(before)<=fast(after)<=total(after)
   row=dict(tag=tag,boxes=after[4]-before[4],fast_rows=after[5]-before[5],slow_rows=after[6]-before[6],bytes=total(after)-total(before),fast_bytes=fast(after)-fast(before))
   assert row['fast_bytes']<=row['bytes']
   if not enabled:assert row['fast_rows']==0 and row['fast_bytes']==0
   elif tag>=10:assert row['fast_rows']>0 and row['fast_bytes']>0
   elif tag in [0,1,3,4]:assert row['fast_rows']>=timed[tag]*128 and row['fast_bytes']>=timed[tag]*256*128*4
   (r['cases'] if tag>=10 else r['intervals']).append(row)
  assert sum(v[0].startswith(('DIB_BEFORE_','DIB_AFTER_')) for v in n)==704
  r.update(passed=True,posttiming_checks=3)
 except (AssertionError,ValueError,IndexError,TypeError,KeyError) as e:r['error']=repr(e)
 return r
