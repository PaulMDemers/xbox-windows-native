"""Decode724 private photo by isolated cell components; no expected register values.
Decoder001 preserved: green color cast made one white sample fail strict minRGB180.
This decoder keeps independent components and requires high meanRGB plus a color floor.
Fixed approximate row bands derive from visible geometry only. Keep photo private.
"""
import sys,json,hashlib,statistics,datetime
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
q=K/'photo002.json';assert not q.exists()
im=Image.open(sys.argv[1]).convert('RGB');raw=Path(sys.argv[1]).read_bytes()
r={'passed':False,'photo_sha256':hashlib.sha256(raw).hexdigest(),'size':list(im.size),'rows':[]}
try:
 assert im.size==(1280,960)
 mask={}
 for y in range(200,705):
  for x in range(120,1125):
   rgb=im.getpixel((x,y))
   if max(rgb)<55:mask[x,y]=0
   elif min(rgb)>180:mask[x,y]=1
 found=[]
 while mask:
  start,bit=mask.popitem();stack=[start];pts=[start]
  while stack:
   x,y=stack.pop()
   for z in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
    if mask.get(z,-1)==bit:del mask[z];stack.append(z);pts.append(z)
  if not 100<=len(pts)<=750:continue
  xs,ys=zip(*pts);w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1
  if 14<=w<=30 and 14<=h<=30 and len(pts)>=0.65*w*h:found.append({'center':[sum(xs)/len(xs),sum(ys)/len(ys)],'bit':bit,'box':[min(xs),min(ys),w,h]})
 left=[220,260,300,340,379,418,457,496,535,574,612,650,687]
 right=[217,255,295,333,371,409,447,485,522,559,595,633,668]
 for row in range(13):
  cells=sorted([v for v in found if abs(v['center'][1]-(left[row]+(right[row]-left[row])*(v['center'][0]-146)/960))<12],key=lambda v:v['center'][0])
  assert len(cells)==32,(row,len(cells))
  assert all(24<b['center'][0]-a['center'][0]<40 for a,b in zip(cells,cells[1:]))
  samples=[]
  for col,cell in enumerate(cells):
   x,y=map(round,cell['center']);variants=[]
   for dx,dy in [(0,0),(-3,0),(3,0),(0,-3),(0,3)]:
    pixels=[im.getpixel((x+dx+u,y+dy+v)) for u in range(-2,3) for v in range(-2,3)]
    rgb=[statistics.median(p[k] for p in pixels) for k in range(3)]
    thresholds=[0 if max(rgb)<b else 1 if sum(rgb)/3>w and min(rgb)>low else None for b,w,low in [(55,185,145),(65,180,140),(75,175,135)]]
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
   rgb=im.getpixel((x,y));bit=0 if max(rgb)<65 else 1 if sum(rgb)/3>180 and min(rgb)>140 else None
   assert bit==r['rows'][row]['samples'][col]['bit'],('cross-row',row,col,rgb)
  cross.append(row)
 r['cross_row_verified']=cross;r['decoded_rows']=[v['value_hex'] for v in r['rows']]
 assert r['decoded_rows'][0]=='0x7240000d','wrong schema/signature'
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();q.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'decoded_rows':r['decoded_rows'],'cross_rows':cross}))
