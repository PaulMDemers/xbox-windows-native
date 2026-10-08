"""Equal-area geometry and strict functional/counter/timer protocol."""
import struct
W,H=768,384
GEOMETRIES=[(192, 96, 0, 0, 0), (192, 96, 0, 128, 0), (192, 96, 0, 0, 160), (192, 96, 3, 0, 0), (192, 96, 3, 128, 0), (192, 96, 3, 0, 160), (192, 96, 4, 0, 0), (192, 96, 4, 128, 0), (192, 96, 4, 0, 160), (64, 96, 0, 320, 64), (128, 96, 0, 320, 64), (192, 96, 0, 320, 64), (256, 96, 0, 320, 64), (320, 96, 0, 320, 64), (384, 96, 0, 320, 64)]
SIZES=[(w,h) for w,h,kind,x,y in GEOMETRIES]
KINDS=['solid','horizontal4','vertical4','horizontal16','vertical16']
CASES=list(range(45))
HOOKS=['BitBlt','CopyBits','TextOut','StrokePath','FillPath','StrokeAndFillPath','LineTo','Paint','StretchBlt','StretchBltROP','PlgBlt','AlphaBlend','GradientFill','TransparentBlt']
def identity(sample):
 cell=(sample%15+(sample//15)*5)%15
 return cell,GEOMETRIES[cell][2]
def rectangles(sample):
 cell,kind=identity(sample);w,h,kind,x,y=GEOMETRIES[cell];n=1 if kind==0 else 4 if kind<=2 else 16
 if kind==0:return [(x,y,x+w,y+h)]
 if kind in [2,4]:return [(x+i*2*(w//n),y,x+i*2*(w//n)+w//n,y+h) for i in range(n)]
 return [(x,y+i*2*(h//n),x+w,y+i*2*(h//n)+h//n) for i in range(n)]

def fnv(data):
 v=2166136261
 for b in data:v=((v^b)*16777619)&0xffffffff
 return v
def base(x,y):return ((x*3+y*5)&255)<<16|((x*7+y*11)&255)<<8|((x*13+y*17)&255)
def expected_bytes(index):
 pixels=[base(x,y) for y in range(H) for x in range(W)]
 for l,t,r,b in rectangles(index):
  for y in range(t,b):pixels[y*W+l:y*W+r]=[0x2bc757]*(r-l)
 return struct.pack('<%dI'%(W*H),*pixels)
def validate_log(data,candidate=True):
 result=dict(passed=False,cases=[],profile_attribution_passed=False,timing_passed=False)
 if data is None:return result
 try:
  lines=data.decode('ascii').splitlines();at=0
  def take(label,exact=None):
   nonlocal at
   row=lines[at].split();at+=1;assert len(row)==4 and row[0]==label,(label,row)
   nums=list(map(int,row[1:]));assert all(0<=v<=0xffffffff for v in nums)
   if exact is not None:assert nums==exact,(label,nums,exact)
   return nums
  def wide(row):return row[0]|row[1]<<32
  take('ATTEMPT_ONCE',[141,45,W*H]);take('INSTALL_IDLE_START',[0,0,0]);take('DRIVER_REVISION_GEOMETRY',[112,1024,576])
  frequency=wide(take('CLOCK_FREQUENCY'));minimum=wide(take('CLOCK_MIN'));maximum=wide(take('CLOCK_MAX'));reads,zeros,negatives=take('CLOCK_READS');tickmin=take('TICK_MIN')[0]
  assert frequency>0 and reads==8192 and zeros<8192 and negatives==0 and 0<minimum<=maximum<2**63
  cross=[]
  for i in range(3):
   q=take('SLEEP_QPC');j,ms,z=take('SLEEP_TICK');assert q[2]==j==i and z==0 and ms>=150
   qms=wide(q)*1000/frequency;cross.append(dict(qpc_ticks=wide(q),tick_ms=ms,consistent=abs(qms-ms)<=max(31,ms*.1)))
  result['clock']=dict(frequency=frequency,minimum_observed_increment=minimum,maximum_observed_increment=maximum,zero_reads=zeros,tick_minimum_observed=None if tickmin==0xffffffff else tickmin,cross_checks=cross)
  for sample in range(45):
   size,kind=identity(sample);w,h=SIZES[size];rects=rectangles(sample);take('CASE',[sample,size,kind]);take('LAYOUT',[w,h,len(rects)]);take('ORIGIN',[GEOMETRIES[size][3],GEOMETRIES[size][4],size])
   typ,left,top=take('CLIP_TYPE_LEFT_TOP');right,bottom,index=take('CLIP_RIGHT_BOTTOM');assert typ==2 and left==top==0 and right>=W and bottom>=H and index==sample
   phases=[]
   for target in ([1,0] if sample&1 else [0,1]):
    idx,which,loops=take('PHASE');assert idx==sample and which==target and 32<=loops<=65536 and loops&(loops-1)==0
    warm,cal,threshold=take('CALIBRATION');assert warm==8 and threshold==500 and cal==2*loops-32
    q=take('DURATION_QPC');ms,z1,z2=take('DURATION_MS');ticks=wide(q);assert q[2]==z1==z2==0 and ticks>0
    pre={};post={};quiet=True
    for i in range(2,19):
     j,a,b=take('QUIET_COUNTER');assert i==j;quiet &= a==b
     j,c,d=take('DRAW_COUNTER');assert i==j and b==c;pre[i]=c;post[i]=d
    take('COHERENCE_ACTIVE',[0,1,0]);calls=[post[i]-pre[i] for i in range(2,16)];uploads=post[16]-pre[16];byte_count=(post[18]<<32|post[17])-(pre[18]<<32|pre[17])
    assert all(0<=pre[i]<=post[i]<0xffffffff for i in range(2,17))
    assert calls==([loops]+[0]*13 if target else [0]*14) and uploads==(loops*len(rects) if target else 0) and byte_count==(loops*w*h*4 if target else 0)
    qms=ticks*1000/frequency;timing=ms>=250 and abs(qms-ms)<=max(31,ms*.1)
    phases.append(dict(target='primary' if target else 'memory',loops=loops,warmup=warm,calibration_loops=cal,qpc_ticks=ticks,tick_ms=ms,qpc_ms=qms,us_per_draw=ticks*1e6/frequency/loops,callbacks=calls,uploads=uploads,upload_bytes=byte_count,quiet=quiet,timing_passed=timing))
   pixels,bad,changed=take('PIXELS_BAD_CHANGED');assert pixels==W*H and bad==0 and changed==w*h
   digest,length,again=take('REFERENCE_HASH_BYTES');assert digest==again and length==W*H*4
   result['cases'].append(dict(index=sample,size=size,x=GEOMETRIES[size][3],y=GEOMETRIES[size][4],kind=KINDS[kind],area=w*h,rectangles=len(rects),row_copies_per_draw=sum(b-t for l,t,r,b in rects),reference_hash=digest,pixels=pixels,mismatches=bad,phases=phases,passed=True))
  take('RELEASED',[1,0,0]);assert wide(take('CLOCK_FREQUENCY_END'))==frequency;take('COMPLETE',[0,45,45*W*H]);take('INSTALL_IDLE_END',[0,0,0]);take('NORMAL_RESTART_REQUEST',[0,0,0]);assert at==len(lines)
  totals=[sum(p['callbacks'][i] for c in result['cases'] for p in c['phases']) for i in range(14)]
  result.update(passed=True,compared_pixels=45*W*H,callback_totals=dict(zip(HOOKS,totals)),unobserved_hooks=[n for n,v in zip(HOOKS,totals) if not v],profile_attribution_passed=all(p['quiet'] for c in result['cases'] for p in c['phases']),timing_passed=all(c['consistent'] for c in cross) and all(p['timing_passed'] for c in result['cases'] for p in c['phases']))
 except (AssertionError,ValueError,IndexError,UnicodeError) as exc:result['error']=repr(exc)
 return result
