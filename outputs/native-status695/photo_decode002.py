"""Optical bit-cell decoder; no expected register values supplied.
Connected black/white cell components avoid perspective calibration from the
screen bezel. Require32 separate cells per row and stable bits at three thresholds.
The source photo remains private. This is optical evidence, not a register dump.
"""
import datetime,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
assert len(sys.argv)==2
raw=Path(sys.argv[1]).read_bytes();im=Image.open(sys.argv[1]).convert('RGB')
out=K/'photo002.json';assert not out.exists()
r={'passed':False,'scope':__doc__,'photo_sha256':hashlib.sha256(raw).hexdigest(),'size':list(im.size),'variants':[]}
try:
 for black,white in [(105,150),(95,160),(115,140)]:
  mask={}
  for y in range(320,580):
   for x in range(160,1100):
    v=im.getpixel((x,y))
    if max(v)<black:mask[x,y]=0
    elif min(v)>white:mask[x,y]=1
  components=[]
  while mask:
   start,v=mask.popitem();stack=[start];points=[start]
   while stack:
    x,y=stack.pop()
    for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
     if mask.get(q,-1)==v:del mask[q];stack.append(q);points.append(q)
   if len(points)<200:continue
   xs,ys=zip(*points);w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1
   if 14<=w<=40 and 20<=h<=45:
    components.append({'center':[sum(xs)/len(xs),sum(ys)/len(ys)],'bit':v,'box':[min(xs),min(ys),w,h],'pixels':len(points)})
  rows=[];used=[]
  for row in range(4):
   # Approximate row-center lines observed from cell geometry, not data values.
   left=[382,444,502,558][row];right=[345,400,453,506][row]
   cells=sorted([v for v in components if abs(v['center'][1]-(left+(right-left)*(v['center'][0]-184)/887))<15],key=lambda v:v['center'][0])
   assert len(cells)==32,(row,len(cells))
   assert all(20<b['center'][0]-a['center'][0]<36 for a,b in zip(cells,cells[1:]))
   bits=''.join(str(v['bit']) for v in cells)
   rows.append({'row':row,'bits_msb_left':bits,'value_hex':f'0x{int(bits,2):08x}','cells':cells})
   used.extend(tuple(v['box']) for v in cells)
  assert len(set(used))==128
  r['variants'].append({'black_max':black,'white_min':white,'rows':rows})
 values=[[v['value_hex'] for v in variant['rows']] for variant in r['variants']]
 assert values[0]==values[1]==values[2]
 r['decoded_rows']=values[0]
 r['bar_samples']=[{'pixel':[1000,y],'rgb':list(im.getpixel((1000,y)))} for y in [200,280]]
 for s in r['bar_samples']:
  red,green,blue=s['rgb'];assert green>160 and red<100 and blue<100
 r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'values':r['decoded_rows'],'bars':r['bar_samples']}))
