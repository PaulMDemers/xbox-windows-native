"""Decode817 private photo from isolated cells without expected values in classification.
Source-only804 decoder; fresh ROI70..1200,190..765. Perspective row assignment from photographed top/bottom cell-center lines; no expected bits.
Geometry calibrated to new817 photograph; no expected bit values used for classification. All thresholds, component geometry,416bits and independent sample checks retained.
"""
import sys,json,hashlib,statistics,datetime
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
q=K/'photo001.json';assert not q.exists()
im=Image.open(sys.argv[1]).convert('RGB');raw=Path(sys.argv[1]).read_bytes()
r={'passed':False,'photo_sha256':hashlib.sha256(raw).hexdigest(),'size':list(im.size),'rows':[]}
try:
 assert im.size==(1280,960)
 mask={}
 for y in range(190,765):
  for x in range(70,1200):
   rgb=im.getpixel((x,y))
   if max(rgb)<100 and sum(rgb)/3<70:mask[x,y]=0
   elif min(rgb)>150 and sum(rgb)/3>180:mask[x,y]=1
 found=[]
 while mask:
  start,bit=mask.popitem();stack=[start];pts=[start]
  while stack:
   x,y=stack.pop()
   for z in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
    if mask.get(z,-1)==bit:del mask[z];stack.append(z);pts.append(z)
  if not 150<=len(pts)<=1200:continue
  xs,ys=zip(*pts);w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1
  if 12<=w<=38 and 12<=h<=38 and len(pts)>=0.65*w*h:found.append({'center':[sum(xs)/len(xs),sum(ys)/len(ys)],'bit':bit,'box':[min(xs),min(ys),w,h]})
 groups=[[] for _ in range(13)];rejected=[]
 for v in found:
  x,y=v['center'];top=209+12*(x-90)/1090;bottom=752-17*(x-90)/1090
  pos=(y-top)*12/(bottom-top);row=round(pos)
  if not (0<=row<13 and abs(pos-row)<0.16):
   assert abs(pos-row)>0.3,('ambiguous row',x,y,pos)
   rejected.append(dict(v,row_position=pos));continue
  v['row_position']=pos;groups[row].append(v)
 assert len(groups)==13,('row-count',len(groups))
 for row in range(13):
  cells=sorted(groups[row],key=lambda v:v['center'][0])
  assert len(cells)==32,(row,len(cells))
  assert all(24<b['center'][0]-a['center'][0]<43 for a,b in zip(cells,cells[1:]))
  samples=[]
  for col,cell in enumerate(cells):
   x,y=map(round,cell['center']);variants=[]
   for dx,dy in [(0,0),(-2,0),(2,0),(0,-2),(0,2)]:
    pixels=[im.getpixel((x+dx+u,y+dy+v)) for u in range(-1,2) for v in range(-1,2)]
    rgb=[statistics.median(p[k] for p in pixels) for k in range(3)]
    thresholds=[0 if max(rgb)<b and sum(rgb)/3<100 else 1 if sum(rgb)/3>w and min(rgb)>low else None for b,w,low in [(135,185,145),(140,180,140),(145,175,135)]]
    assert thresholds==[cell['bit']]*3,(row,col,rgb)
    variants.append({'offset':[dx,dy],'median_rgb':rgb})
   samples.append({'column':col,'center':[x,y],'bit':cell['bit'],'variants':variants})
  bits=''.join(str(v['bit']) for v in samples)
  r['rows'].append({'row':row,'bits_msb_left':bits,'value_hex':f'0x{int(bits,2):08x}','samples':samples})
 # Geometry independent of each middle row: interpolate adjacent-row centers.
 cross=[]
 for row in range(1,12):
  for col in range(32):
   a=r['rows'][row-1]['samples'][col]['center'];b=r['rows'][row+1]['samples'][col]['center'];x,y=[round((a[i]+b[i])/2) for i in range(2)]
   rgb=im.getpixel((x,y));bit=0 if max(rgb)<140 and sum(rgb)/3<100 else 1 if sum(rgb)/3>180 and min(rgb)>140 else None
   assert bit==r['rows'][row]['samples'][col]['bit'],('cross-row',row,col,rgb)
  cross.append(row)
 r['off_grid_components_rejected']=rejected;r['cross_row_verified']=cross;r['decoded_rows']=[v['value_hex'] for v in r['rows']]
 assert r['decoded_rows'][0]=='0x8170000d','wrong schema/signature'
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();q.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'decoded_rows':r['decoded_rows'],'cross_rows':cross}))
