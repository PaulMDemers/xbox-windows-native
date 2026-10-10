"""Fail-closed119 packet/phase parser; NULL bytes describe input bounds, not waste."""
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt','SurfaceLifecycle']
FIELDS=['requests','explicit_rect','null_rect','boxes','bytes','null_bytes','fallbacks']
def packet(values,enabled):
 assert len(values)==158 and all(type(v)==int and 0<=v<=0xffffffff for v in values)
 assert values[:8]==[0x41555758,119,632,enabled,15,0,0,0]
 rows=[]
 for kind in range(15):
  a=values[8+kind*10:18+kind*10];assert a[9]==0
  b=a[4]+(a[5]<<32);z=a[6]+(a[7]<<32)
  assert a[0]==a[1]+a[2] and z<=b and a[8]<=a[0]
  assert (a[3]==0)==(b==0) and b%4==0 and z%4==0
  assert all(v<0xffffffff for v in [a[0],a[1],a[2],a[3],a[8]]) and b<0xffffffffffffffff
  if not enabled:assert not any(a)
  rows.append(dict(zip(FIELDS,[a[0],a[1],a[2],a[3],b,z,a[8]])))
 return rows
def analyze(log,enabled):
 r=dict(passed=False,enabled=enabled,steps=[],phase_totals={label:{name:{f:0 for f in FIELDS} for name in HOOKS} for label in ['move','paint','readback']},
        limits='Device-global completed-copy counters in fixed phase windows. Background/chrome/exposure included; NULL rectangle is not automatically redundant. No speed or FPS claim.')
 try:
  raw=[v.split() for v in (log or '').splitlines()];assert all(len(v)==4 for v in raw)
  nums=[(v[0],*[int(x) for x in v[1:]]) for v in raw]
  assert [v for v in nums if v[0]=='UPLOAD_STEP_exact']==[('UPLOAD_STEP_exact',i,1,0) for i in range(40)]
  words=[v for v in nums if v[0]=='UPLOAD_WORD_tag_index_value']
  assert len(words)==40*4*158
  expected=[(tag,j) for tag in range(160) for j in range(158)]
  assert [(v[1],v[2]) for v in words]==expected
  packets=[packet([v[3] for v in words[tag*158:(tag+1)*158]],enabled) for tag in range(160)]
  for step in range(40):
   item=dict(step=step,phases={})
   for phase,label in enumerate(['move','paint','readback'],1):
    before,after=packets[step*4+phase-1:step*4+phase+1];delta=[]
    for kind,name in enumerate(HOOKS):
     row={f:after[kind][f]-before[kind][f] for f in FIELDS};assert all(v>=0 for v in row.values())
     assert row['requests']==row['explicit_rect']+row['null_rect'] and row['null_bytes']<=row['bytes']
     assert (row['boxes']==0)==(row['bytes']==0)
     delta.append(dict(kind=name,**row))
     for f in FIELDS:r['phase_totals'][label][name][f]+=row[f]
    item['phases'][label]=delta
   if enabled:
    paint=item['phases']['paint'];assert sum(paint[i]['requests'] for i in [0,1])>=1 and sum(paint[i]['bytes'] for i in [0,1])>=256*128*4
    assert paint[2]['requests']>=1 and paint[2]['bytes']>0
   r['steps'].append(item)
  r['total_upload_bytes']=sum(v['bytes'] for phase in r['phase_totals'].values() for v in phase.values())
  r['total_null_request_bytes']=sum(v['null_bytes'] for phase in r['phase_totals'].values() for v in phase.values())
  if enabled:assert r['total_upload_bytes']>0
  else:assert r['total_upload_bytes']==0
  r.update(passed=True,completed_steps=40,actual_phase_pairs=120,packet_count=160)
 except (AssertionError,ValueError,KeyError,IndexError,TypeError) as e:r['error']=repr(e)
 return r
