"""Strict pixel protocol plus separate upload attribution gates (not a speed test)."""
import struct
KINDS=['small_fill','unclipped_line','tight_clip_line','overlap_copy','disjoint_clip_fill','small_stretch']
CASES=[f'{n}_{r}' for r in range(3) for n in KINDS]
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
def fnv(data):
 v=2166136261
 for b in data:v=((v^b)*16777619)&0xffffffff
 return v
def expected_bytes(index):
 assert 0<=index<18
 pixels=[((x*3+y*5)&255)<<16|((x*7+y*11)&255)<<8|((x*13+y*17)&255) for y in range(256) for x in range(384)]
 original=pixels[:];kind=index%6
 for y in range(256):
  for x in range(384):
   color=None
   if kind in (0,5) and 20<=x<52 and 20<=y<36:color=0x2bc757
   if kind in (1,2) and 20<=x<52 and y==20:color=0xdd2597
   if kind==3 and 40<=x<168 and 40<=y<136:color=original[(y-20)*384+x-20]
   if kind==4 and ((20<=x<36 and 20<=y<36) or (200<=x<216 and 160<=y<176)):color=0x2bc757
   if color is not None:pixels[y*384+x]=color
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
  take('ATTEMPT_ONCE',[128,18,98304]);take('INSTALL_IDLE_START',[0,0,0]);take('DRIVER_REVISION_GEOMETRY',[109,1024,576])
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
   passed=a==b==1 and bad==0 and changed==[512,32,32,12288,512,512][index%6] and digest==again and source[0]==source[1] and source[2]==0 and coherent
   r['cases'].append(dict(index=index,name=name,passed=passed,reference_hash=digest,pixels=pixels,mismatches=bad,changed_pixels=changed,callbacks=calls,uploads=uploads,upload_bytes=byte_count,quiet=quiet,reference_quiet=refquiet,monotonic=monotonic,clip=[left,top,right,bottom]))
  take('RELEASED',[1,0,0]);take('COMPLETE',[0,18,18*98304]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
  samples=r['cases'];repeat=all(all(samples[i][field]==samples[i+delta][field] for field in ['callbacks','uploads','upload_bytes','clip']) for i in range(6) for delta in [6,12])
  totals=[sum(v['callbacks'][i] for v in samples) for i in range(14)]
  attribution=repeat and all(v['quiet'] and v['reference_quiet'] and v['monotonic'] and v['uploads']>0 and v['upload_bytes']>0 for v in samples)
  r.update(passed=all(v['passed'] for v in samples),completed=True,compared_pixels=18*98304,callback_totals=dict(zip(HOOKS,totals)),unobserved_hooks=[n for n,v in zip(HOOKS,totals) if not v],repeat_identical=repeat,profile_attribution_passed=attribution)
 except (AssertionError,ValueError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
 return r
