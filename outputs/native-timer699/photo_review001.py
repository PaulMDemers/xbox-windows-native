"""Independent adjacent-row geometry check of this run's private photograph."""
from pathlib import Path
import sys,json,hashlib,datetime,statistics
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
q=K/'photo-review001.json'
assert not q.exists()
d=json.loads((K/'photo001.json').read_text())
raw=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(raw).hexdigest()==d['photo_sha256']
im=Image.open(sys.argv[1]).convert('RGB')
r={'passed':False,'photo_sha256':d['photo_sha256'],'decode_receipt_sha256':hashlib.sha256((K/'photo001.json').read_bytes()).hexdigest(),'cross_row_results':[]}
try:
 for row in range(1,9):
  bits=[]
  for col in range(32):
   a=d['rows'][row-1]['samples'][col]['center']; b=d['rows'][row+1]['samples'][col]['center']
   x,y=[round((a[i]+b[i])/2) for i in range(2)]
   pixels=[im.getpixel((x+u,y+v)) for u in range(-2,3) for v in range(-2,3)]
   rgb=[statistics.median(p[k] for p in pixels) for k in range(3)]
   bit=0 if max(rgb)<95 else 1 if min(rgb)>160 else None
   assert bit is not None and bit==d['rows'][row]['samples'][col]['bit'],(row,col,rgb)
   bits.append(str(bit))
  r['cross_row_results'].append({'row':row,'value_hex':f'0x{int("".join(bits),2):08x}'})
 values=[int(v,16) for v in d['decoded_rows']]
 assert ((values[4]-values[3])&0xffffffff)==values[5]
 r['values']=dict(zip(['pci_id','pci_command_status','pci_bar','first_tick','last_tick','elapsed_ticks','timer_read_count','result_code','tsc_delta_low','tsc_delta_high'],values))
 r['elapsed_arithmetic_checked']=True
 r['nominal_interval_us_at_kernel_reported_3375000_hz']=values[5]*1000000/3375000
 r['scope']='Optical evidence; 320 bits threshold/offset checked and middle 256 bits cross-row checked. No independent clock calibration or serialized TSC measurement.'
 r['passed']=True
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 q.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
