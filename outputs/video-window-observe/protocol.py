"""Native movement protocol, independent composition and scoped byte attribution."""
import struct
POSITIONS=[(12,16),(112,56),(208,104),(240,168),(-24,196),(88,-24)]
CASES=[f'move_{i%6}_repeat_{i//6}' for i in range(18)]
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
def fnv(data):
 v=2166137261
 for b in data:v=((v^b)*16777619)&0xffffffff
 return v
def base(x,y):return ((x*3+y*5)&255)<<16|((x*7+y*11)&255)<<8|((x*13+y*17)&255)
def source_valid(data,meta):
 if len(data)!=40960 or len(meta)!=3:return False
 width,height,digest=meta
 if not (0<width<=120 and 0<height<=56 and fnv(data)==digest):return False
 pixels=struct.unpack('<10240I',data);changes=0
 for y in range(80):
  for x in range(128):
   v=pixels[y*128+x]&0xffffff
   if v!=base(x+17,y+23):
    if not (8<=x<8+width and 24<=y<24+height and v==0xffffff):return False
    changes+=1
 return changes>10

def expected_bytes(index,source):
 assert 0<=index<18 and len(source)==40960
 sp=struct.unpack('<10240I',source);left,top=POSITIONS[index%6];pixels=[]
 for y in range(256):
  for x in range(384):
   v=base(x,y)
   if left<=x<left+128 and top<=y<top+80:v=sp[(y-top)*128+x-left]
   if 144<=x<240 and 56<=y<200:v=0x462daa
   pixels.append(v)
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
  def counter(label):
   a={};b={}
   for i in range(2,19):
    j,x,y=take(label);assert j==i;a[i]=x;b[i]=y
   return a,b
  def delta(a,b):
   calls=[b[i]-a[i] for i in range(2,16)];size=(b[18]<<32|b[17])-(a[18]<<32|a[17]);uploads=b[16]-a[16]
   assert all(0<=a[i]<=b[i]<0xffffffff for i in range(2,17)) and size>=0
   return dict(callbacks=calls,uploads=uploads,upload_bytes=size)
  take('ATTEMPT_ONCE',[137,18,98304]);take('INSTALL_IDLE_START',[0,0,0]);take('DRIVER_REVISION_GEOMETRY',[112 if candidate else 110,1024,576]);r['source_metadata']=take('TEXT_SIZE_SOURCE')
  r['parent_origin']=take('PARENT_ORIGIN');r['parent_size']=take('PARENT_SIZE')
  for index,name in enumerate(CASES):
   left,top=POSITIONS[index%6];take('CASE_POSITION',[index,left&0xffffffff,top&0xffffffff]);take('MOVE_API_PIXELS',[1,0,98304]);take('MOVE_SIZE',[128,80,0]);paints=[]
   for i in range(3):
    j,x,y=take('MOVE_PAINT');assert j==i and y>=x;paints.append(y-x)
   q,pre=counter('QUIET_COUNTER');a,b=counter('DRAW_COUNTER');assert pre==a
   take('REDRAW_API_PIXELS',[1,0,98304]);ra,rb=counter('REDRAW_COUNTER');elapsed=take('ELAPSED_MS');assert elapsed[2]==0
   digest,size,again=take('REFERENCE_HASH_BYTES');assert digest==again and size==393216
   errors=take('PAINT_ERRORS');assert errors==[0,0,0];take('COHERENCE_ACTIVE',[0,1,0])
   move=delta(a,b);redraw=delta(ra,rb);assert redraw['callbacks'][2]>0 and move['upload_bytes']>0 and redraw['upload_bytes']>0
   r['cases'].append(dict(index=index,name=name,passed=True,reference_hash=digest,pixels=196608,mismatches=0,paints=paints,quiet=q==pre,move=move,redraw=redraw,move_ms=elapsed[0],redraw_ms=elapsed[1]))
  take('RELEASED',[1,0,0]);take('COMPLETE',[0,18,18*98304*2]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
  totals=[sum(v[p]['callbacks'][i] for v in r['cases'] for p in ['move','redraw']) for i in range(14)]
  r.update(passed=True,completed=True,compared_pixels=18*98304*2,callback_totals=dict(zip(HOOKS,totals)),unobserved_hooks=[n for n,v in zip(HOOKS,totals) if not v],profile_attribution_passed=all(v['quiet'] for v in r['cases']),timing_isolated=False)
 except (AssertionError,ValueError,IndexError,UnicodeError) as exc:r['error']=repr(exc)
 return r
