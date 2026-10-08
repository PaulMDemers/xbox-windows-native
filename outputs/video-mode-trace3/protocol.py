CASES=['solid_patcopy','hatch_patinvert','srcinvert','maskblt','stretch','mirrored_stretch','plgblt','masked_plgblt','line','dashed_polyline','stroke_bezier_path','fill_polygon_path','stroke_fill_ellipse_path','paint_region','opaque_text','transparent_text','gradient_rectangle','gradient_triangle','constant_alpha','pixel_alpha','transparent_blt','24bit_translation','complex_clip','empty_clip','offscreen_clip','hatch_roundrect']
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
def fnv(data):
 value=2166136261
 for byte in data:value=((value^byte)*16777619)&0xffffffff
 return value
def validate_log(data,candidate=True):
 r=dict(passed=False,cases=[])
 if data is None:return r
 try:
  lines=data.decode('ascii').splitlines();at=0
  def take(label,exact=None):
   nonlocal at
   words=lines[at].split();at+=1;assert words[0]==label and len(words)==4,(label,words)
   nums=list(map(int,words[1:]))
   if exact is not None:assert nums==exact,(label,nums,exact)
   return nums
  take('ATTEMPT_ONCE',[124,26,98304]);take('INSTALL_IDLE_START',[0,0,0]);take('DRIVER_REVISION_GEOMETRY',[109,1024,576]);take('CURSOR_PARKED',[1000,550,0])
  for index,name in enumerate(CASES):
   if index==13:
    take('MODE_CURRENT',[1024,576,32]);detail=take('MODE_CURRENT_DETAIL')
    modes=[]
    while lines[at].startswith('MODE_ENUM '):
     i,width,height=take('MODE_ENUM');assert i==len(modes) and i<128
     bpp,hz,flags=take('MODE_ENUM_DETAIL');modes.append([width,height,bpp,hz,flags])
    take('MODE_ENUM_END',[len(modes),1,1]);assert [1024,576,32,detail[0],detail[1]] in modes
    take('MODE_TEST',[0,2,0]);take('MODE_RESET',[0,0x40000000,0])
    take('MODE_AFTER',[1024,576,32]);after=take('MODE_AFTER_DETAIL');assert after[:2]==detail[:2]
    take('MODE_DRIVER_AFTER',[109,1024,576]);r['mode_reset']=dict(api_success=True,current_detail=detail,after_detail=after,enumerated=modes,lifecycle_coverage='requires independent observer')
   take('CURSOR_OVER_DRAW',[index,[80,0,380,170][index%4],[70,0,250,140][index%4]])
   for phase in range(3):take('CURSOR_PHASE',[index,phase,int(phase!=1)])
   take('CURSOR_RESTORED',[index,1000,550])
   i,a,b=take('CASE_API');assert i==index
   pixels,bad,changed=take('PIXELS_BAD_CHANGED');assert pixels==98304
   digest,length,digest_after=take('REFERENCE_HASH_BYTES');assert length==393216
   source32=take('SOURCE32_HASH_PAIR');source24=take('SOURCE24_HASH_PAIR');coherence=take('COHERENCE_ACTIVE')
   refcalls=[];calls=[]
   for label,counts in [('REFERENCE_CALLBACK_DELTA',refcalls),('CALLBACK_DELTA',calls)]:
    for j in range(14):
     hook,count,z=take(label);assert hook==j and z==0;counts.append(count)
   passed=a==b==1 and not bad and (changed==0 if index==23 else changed>0) and digest==digest_after and not any(refcalls) and coherence==[0,1,0] and all(v[0]==v[1] and v[2]==0 for v in [source32,source24])
   r['cases'].append(dict(index=index,name=name,passed=passed,api=[a,b],pixels=pixels,mismatches=bad,changed_pixels=changed,reference_hash=digest,reference_hash_after=digest_after,source32=source32,source24=source24,coherence=coherence,reference_callbacks=refcalls,callbacks=calls))
  take('RELEASED',[1,0,0]);failures,n,pixels=take('COMPLETE');assert n==26 and pixels==26*98304
  take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
  totals=[sum(v['callbacks'][i] for v in r['cases']) for i in range(14)]
  r.update(passed=not failures and all(v['passed'] for v in r['cases']),completed=True,failures=failures,verified_pixel_stages=26,compared_pixels=26*98304,callback_totals=dict(zip(HOOKS,totals)),unobserved_hooks=[n for n,v in zip(HOOKS,totals) if not v])
 except (AssertionError,ValueError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
 return r
