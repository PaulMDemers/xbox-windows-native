"""Decode the four photographed MSB-left bit rows. No expected register values input.
Project screen coordinates through manually selected inner-screen corners;
sample centers, reject ambiguous luminance, and check small sampling offsets.
The photo stays private. This is optical evidence, not a memory/register dump.
"""
import datetime,hashlib,json,statistics,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
assert len(sys.argv)==2
p=Path(sys.argv[1]);raw=p.read_bytes();im=Image.open(p).convert('RGB')
out=K/'photo001.json';assert not out.exists()
corners=[(27,179),(1187,158),(1150,742),(111,827)]
source=[(0,0),(1279,0),(1279,719),(0,719)]
a=[]
for (x,y),(u,v) in zip(source,corners):
 a.extend([[x,y,1,0,0,0,-u*x,-u*y,u],[0,0,0,x,y,1,-v*x,-v*y,v]])
for i in range(8):
 j=max(range(i,8),key=lambda j:abs(a[j][i]));a[i],a[j]=a[j],a[i]
 d=a[i][i];assert abs(d)>1e-9;a[i]=[v/d for v in a[i]]
 for j in range(8):
  if j!=i:
   d=a[j][i];a[j]=[v-d*w for v,w in zip(a[j],a[i])]
h=[row[-1] for row in a]
def project(x,y):
 den=h[6]*x+h[7]*y+1
 return ((h[0]*x+h[1]*y+h[2])/den,(h[3]*x+h[4]*y+h[5])/den)
def sample(x,y):
 px,py=project(x,y);ix,iy=round(px),round(py)
 values=[im.getpixel((ix+dx,iy+dy)) for dx in [-1,0,1] for dy in [-1,0,1]]
 rgb=[statistics.median(v[c] for v in values) for c in range(3)]
 return {'pixel':[round(px,2),round(py,2)],'rgb':rgb,'luminance':sum(rgb)/3}
r={'passed':False,'scope':__doc__,'photo_sha256':hashlib.sha256(raw).hexdigest(),
 'photo_size':list(im.size),'screen_corners_pixels':corners,'rows':[]}
try:
 for row in range(4):
  samples=[];bits=[]
  for col in range(32):
   x,y=128+32*col+12,200+64*row+16
   v=sample(x,y);lum=v['luminance'];assert lum<70 or lum>160,('ambiguous',row,col,v)
   bit=int(lum>160)
   for dx,dy in [(-3,0),(3,0),(0,-3),(0,3)]:
    q=sample(x+dx,y+dy)['luminance'];assert (q<70 if not bit else q>160)
   bits.append(str(bit));samples.append(v)
  r['rows'].append({'row':row,'bits_msb_left':''.join(bits),'value_hex':f'0x{int("".join(bits),2):08x}','samples':samples})
 r['bars']=[sample(1000,y) for y in [40,128]]
 for v in r['bars']:assert v['rgb'][1]>160 and v['rgb'][0]<100 and v['rgb'][2]<100
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'rows':[v['value_hex'] for v in r['rows']],'bars':r['bars']}))
