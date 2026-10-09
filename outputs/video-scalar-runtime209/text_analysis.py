"""Fail closed on all13 actual NT5 pixel/coherence/copy packets; no global timing inference."""
def analyze(log,mode):
 r=dict(passed=False,mode=mode,cases=[],physical_qualified=False)
 try:
  rows=[v.split() for v in (log or '').splitlines()];assert rows and all(len(v)==4 for v in rows)
  n=[(v[0],*[int(x) for x in v[1:]]) for v in rows]
  assert n[0]==('XWN_GDI_PROBE_VERSION',11,256,128) and n[-1]==('PASS',0,0,0)
  assert all(0<=x<=0xffffffff for v in n for x in v[1:])
  assert not any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in n)
  assert [v for v in n if v[0]=='TEXT_CASE_case_pass']==[('TEXT_CASE_case_pass',i,1,0) for i in range(13)]
  assert [v for v in n if v[0]=='TEXT_DRAW_case_result_packets']==[('TEXT_DRAW_case_result_packets',i,1,1) for i in range(13)]
  assert [v for v in n if v[0]=='TEXT_SCANOUT_case_result_mismatches']==[('TEXT_SCANOUT_case_result_mismatches',i,1,0) for i in range(13)]
  assert sum(v[0].startswith(('TEXT_BEFORE_','TEXT_AFTER_')) for v in n)==13*80
  j=lambda a,i:a[i]+(a[i+1]<<32)
  for case in range(13):
   pair=[]
   for label in ['TEXT_BEFORE_case_index_value','TEXT_AFTER_case_index_value']:
    v=[q for q in n if q[0]==label and q[1]==case]
    assert len(v)==40 and [q[2] for q in v]==list(range(40))
    a=[q[3] for q in v];assert a[:4]==[0x54585758,118,160,mode] and not a[11] and not a[29] and a[30:32]==[0,0] and a[38:]==[0,0] and a[37] in [0,1] and a[36] in [0,1,3]
    assert a[4]<0xffffffff and a[8]<0xffffffff and j(a,9)<(1<<64)-1
    pair.append(a)
   b,a=pair;calls=a[4]-b[4];assert calls==1 or (case==3 and calls==0)
   assert all(a[i]>=b[i] for i in list(range(4,9))+list(range(12,19))) and j(a,9)>=j(b,9)
   expected=[q for q in n if q[0]=='TEXT_EXPECTED_case_bytes_delta' and q[1]==case];assert len(expected)==1 and expected[0][3]==calls
   pixel=[q for q in n if q[0]=='TEXT_PIXELS_case_changed_guard' and q[1]==case];assert len(pixel)==1 and pixel[0][2]>0 and pixel[0][3]>0 and pixel[0][2]+pixel[0][3]==256*128
   fm=[q for q in n if q[0]=='TEXT_FONT_case_italic_underline' and q[1]==case];fs=[q for q in n if q[0]=='TEXT_FONT_case_strike_height' and q[1]==case]
   assert len(fm)==len(fs)==1 and fs[0][3]>0
   if case==4:assert fm[0][2]>0
   if case==5:assert fm[0][3]>0
   if case==6:assert fs[0][2]>0
   geo=[q for q in n if q[0]=='TEXT_CLIENT_case_width_height' and q[1]==case];origin=[q for q in n if q[0]=='TEXT_ORIGIN_case_x_y' and q[1]==case]
   assert len(geo)==len(origin)==1 and 256<=geo[0][2]<=1024 and 128<=geo[0][3]<=1024
   assert origin[0][2]<1024 and origin[0][3]<1024
   def signed(v):return v if v<0x80000000 else v-(1<<32)
   bound=list(map(signed,a[22:26]));clip=list(map(signed,a[32:36]));ox,oy=origin[0][2:]
   oracle=0
   if calls:
    for y in range(geo[0][3]):
     for x in range(geo[0][2]):
      inside=(case!=10 or 10<=x<133 and 12<=y<73) and (case!=11 or 5<=x<85 and 5<=y<70 or 140<=x<245 and 18<=y<117)
      if a[37]:inside=inside and clip[0]<=x+ox<clip[2] and clip[1]<=y+oy<clip[3]
      if mode:inside=inside and bound[0]<=x+ox<bound[2] and bound[1]<=y+oy<bound[3] and a[20]!=1
      if inside:oracle+=4
   actual=j(a,9)-j(b,9)
   if calls:
    assert a[20] in [0,1] and a[21]==mode and a[26]==a[8]-b[8] and j(a,27)==actual==expected[0][2]==oracle
    assert sum(a[i]-b[i] for i in range(12,19))==1 and a[12+a[20]]-b[12+a[20]]==1
    if mode:assert a[5]-b[5]==(a[20]==0) and a[7]-b[7]==(a[20]==1) and a[6]==b[6]
    else:assert a[6]-b[6]==1 and a[5]==b[5] and a[7]==b[7]
    if case!=3:assert a[19]>0 and actual>0 and a[26]>0
   else:assert actual==0 and a==b
   r['cases'].append(dict(case=case,calls=calls,copied_bytes=actual,copied_boxes=a[8]-b[8],reason=a[20] if calls else None,
                           glyphs=a[19] if calls else None,changed_pixels=pixel[0][2],guard_pixels=pixel[0][3],bounds=a[22:26] if calls else None,input_clip=a[32:36] if calls else None,clip_complexity=a[36] if calls else None,client=geo[0][2:],origin=origin[0][2:]))
  r.update(passed=True,pixel_comparisons=13*256*128,coherence_checks=13,
     limits='Reference RAM DIB versus visible client readback, whole RAM/scanout coherence, immediate117 packet pairing. GDI empty opaque dispatch may bypass TextOut; no invalid metadata or extra rectangle runtime claim. No emulator FPS implies physical speed.')
 except (AssertionError,ValueError,IndexError,TypeError) as exc:r['error']=repr(exc)
 return r
