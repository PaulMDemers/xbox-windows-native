"""Strict pixel protocol plus separate upload attribution gates (not a speed test)."""
import struct
LINES=[(20,20,52,20,0),(52,20,20,20,0),(20,20,20,52,0),(20,52,20,20,0),(20,20,52,52,0),(52,52,20,20,0),(20,52,52,20,0),(52,20,20,52,0),(-20,20,52,20,0),(52,20,-20,20,0),(-20,-20,52,52,0),(52,52,-20,-20,0),(20,20,52,20,1),(52,20,20,20,1),(20,20,220,20,2),(220,20,20,20,2),(380,20,420,20,3),(20,20,20,20,0)]
CASES=['horizontal','reverse_horizontal','vertical','reverse_vertical','diagonal_down','reverse_diagonal_down','diagonal_up','reverse_diagonal_up','left_clipped','reverse_left_clipped','diagonal_clipped','reverse_diagonal_clipped','tight','reverse_tight','complex','reverse_complex','right_clipped','empty']
def points(index):
 x,y,endx,endy,clip=LINES[index];dx=endx-x;dy=endy-y;n=max(abs(dx),abs(dy));assert dx==0 or dy==0 or abs(dx)==abs(dy)
 result=[]
 for i in range(n):
  px=x+(i if dx>0 else -i if dx<0 else 0);py=y+(i if dy>0 else -i if dy<0 else 0)
  if not (0<=px<384 and 0<=py<256):continue
  if clip==1 and not (20<=px<36 and 20<=py<21):continue
  if clip==2 and not (20<=py<36 and (20<=px<36 or 200<=px<216)):continue
  result.append((px,py))
 return result
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
def fnv(data):
 v=2166136261
 for b in data:v=((v^b)*16777619)&0xffffffff
 return v
def expected_bytes(index):
 assert 0<=index<18
 pixels=[((x*3+y*5)&255)<<16|((x*7+y*11)&255)<<8|((x*13+y*17)&255) for y in range(256) for x in range(384)]
 for x,y in points(index):pixels[y*384+x]=0xdd2597
 return struct.pack('<98304I',*pixels)
def validate_log(data,candidate=True):
 r=dict(passed=False,cases=[],profile_attribution_passed=False)
 if data is None:return r
 try:
  lines=data.decode('ascii').splitlines();at=0
  def take(label,exact=None):
   nonlocal at
   words=lines[at].split();at+=1;assert len(words)==4 and words[0]==label,(label,words)
   nums=list(map(int,words[1:]));assert all(0<=v<=0xffffffff for v in nums)
   if exact is not None:assert nums==exact,(label,nums,exact)
   return nums
  take('ATTEMPT_ONCE',[130,18,98304]);take('INSTALL_IDLE_START',[0,0,0]);take('DRIVER_REVISION_GEOMETRY',[110 if candidate else 109,1024,576])
  for index,name in enumerate(CASES):
   cliptype,left,top=take('CLIP_TYPE_LEFT_TOP');right,bottom,clipindex=take('CLIP_RIGHT_BOTTOM')
   assert cliptype==2 and left==top==0 and right>=384 and bottom>=256 and clipindex==index
   _,a,b=take('CASE_API');assert _==index
   pixels,bad,changed=take('PIXELS_BAD_CHANGED');assert pixels==98304
   digest,length,again=take('REFERENCE_HASH_BYTES');assert length==393216
   source=take('SOURCE_HASH_PAIR');quiet=True;refquiet=True;before={};after={}
   for i in range(2,19):
    j,x,y=take('QUIET_COUNTER');assert j==i;quiet &= x==y
    j,u,v=take('REFERENCE_COUNTER');assert j==i and u==y;refquiet &= u==v
    j,lo,hi=take('DRAW_COUNTER');assert j==i and lo==v
    before[i]=lo;after[i]=hi
   coherent=take('COHERENCE_ACTIVE')==[0,1,0]
   calls=[after[i]-before[i] for i in range(2,16)]
   uploads=after[16]-before[16]
   byte_count=(after[18]<<32|after[17])-(before[18]<<32|before[17])
   monotonic=all(0<=before[i]<=after[i]<0xffffffff for i in range(2,17)) and byte_count>=0
   passed=a==b==1 and bad==0 and changed==len(points(index)) and digest==again and source[0]==source[1] and source[2]==0 and coherent
   r['cases'].append(dict(index=index,name=name,passed=passed,reference_hash=digest,pixels=pixels,mismatches=bad,changed_pixels=changed,callbacks=calls,uploads=uploads,upload_bytes=byte_count,quiet=quiet,reference_quiet=refquiet,monotonic=monotonic,clip=[left,top,right,bottom]))
  take('RELEASED',[1,0,0]);take('COMPLETE',[0,18,18*98304]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
  samples=r['cases'];repeat=False
  totals=[sum(v['callbacks'][i] for v in samples) for i in range(14)]
  attribution=all(v['quiet'] and v['reference_quiet'] and v['monotonic'] for v in samples)
  r.update(passed=all(v['passed'] for v in samples),completed=True,compared_pixels=18*98304,callback_totals=dict(zip(HOOKS,totals)),unobserved_hooks=[n for n,v in zip(HOOKS,totals) if not v],repeat_identical=repeat,profile_attribution_passed=attribution)
 except (AssertionError,ValueError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
 return r
