"""Independently resample806 photo and map raw cells to the frozen contract."""
from pathlib import Path
import json, hashlib, datetime, sys, statistics
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'photo-review001.json';assert not out.exists()
r={'passed':False,'physical_access':False}
try:
 d=json.loads((K/'photo001.json').read_text())
 schema=json.loads((K/'optical-schema001.json').read_text())
 image=Path('C:/xwn806/photo001.jpg');im=Image.open(image).convert('RGB')
 assert d['passed'] and d['photo_sha256']==sha(image)
 assert len(d['rows'])==13 and d['cross_row_verified']==list(range(1,12))
 black=[];white=[];values=[];cross=0
 for row in d['rows']:
  assert len(row['samples'])==32
  bits=[]
  for c in row['samples']:
   assert len(c['variants'])==5
   x,y=c['center'];bits.append(str(c['bit']))
   for v in c['variants']:
    dx,dy=v['offset']
    pixels=[im.getpixel((x+dx+u,y+dy+w)) for u in range(-1,2) for w in range(-1,2)]
    rgb=[statistics.median(p[i] for p in pixels) for i in range(3)]
    assert rgb==v['median_rgb']
    for b,w,low in [(135,185,145),(140,180,140),(145,175,135)]:
     bit=0 if max(rgb)<b and sum(rgb)/3<100 else 1 if sum(rgb)/3>w and min(rgb)>low else None
     assert bit==c['bit']
    (white if c['bit'] else black).append(rgb)
  value=int(''.join(bits),2);assert value==int(row['value_hex'],16)
  values.append(value)
 for row in range(1,12):
  for col in range(32):
   a=d['rows'][row-1]['samples'][col]['center'];b=d['rows'][row+1]['samples'][col]['center']
   x,y=[round((a[i]+b[i])/2) for i in range(2)];rgb=im.getpixel((x,y))
   bit=0 if max(rgb)<140 and sum(rgb)/3<100 else 1 if sum(rgb)/3>180 and min(rgb)>140 else None
   assert bit==d['rows'][row]['samples'][col]['bit'];cross+=1
 assert values==[int(v,16) for v in d['decoded_rows']]
 fields=dict(zip(schema['names'],values))
 assert fields['signature']==0x8060000d and fields['return_code']==0x806
 assert len(schema['names'][2:10])==8 and all(fields[n]==0 for n in schema['names'][2:10])
 assert [fields[n] for n in ['CR15_blank_before','CR15_blank_after','CR15_blank_restored']]==[207,223,207]
 assert schema['total_masks_required_for_success']==30 and len(schema['omitted_aggregate_masks'])==22
 r.update(passed=True,fields=fields,bits=416,offset_samples_per_bit=5,
  thresholds_per_sample=3,adjacent_row_cross_checks=cross,
  photo_sha256=sha(image),decoder_sha256=sha(K/'photo_decode001.py'),
  decode_sha256=sha(K/'photo001.json'),schema_sha256=sha(K/'optical-schema001.json'),
  reviewer_sha256=sha(Path(__file__)),max_black_channel_median=max(max(v) for v in black),
  min_white_mean_median=min(sum(v)/3 for v in white),
  user_observation='Photo supplied; green bar visible in photo',
  physical_proof='Native CR07 blank-startCF/DF/CF and own-value recovery; photo-only result',
  limits=['Eight displayed recovery masks zero; twenty-two omitted masks aggregate-only via final806; same-value dropped writes indistinguishable',
   'Native neighbor/selector/CPU and earlier individual recovery values not exposed raw',
   'No full mode switch, Windows1.6, acceleration or normal shutdown proof'],
  decode_failures_preserved=[],
  decode_method='Actual isolated pixels; all416 bits at five offsets/three thresholds;352 adjacent-row interpolated samples independently rechecked. No expected values used to classify pixels.')
except BaseException as e:
 r['failure']=repr(e);raise
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'fields':fields,'black_max':r['max_black_channel_median'],'white_min':r['min_white_mean_median']}))
