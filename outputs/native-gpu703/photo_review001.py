"""Independent adjacent-row geometry check of this run's private photograph."""
from pathlib import Path
import sys,json,hashlib,datetime,statistics
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
q=K/'photo-review001.json'
assert not q.exists()
d=json.loads((K/'photo002.json').read_text())
raw=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(raw).hexdigest()==d['photo_sha256']
im=Image.open(sys.argv[1]).convert('RGB')
r={'passed':False,'photo_sha256':d['photo_sha256'],'decode_receipt_sha256':hashlib.sha256((K/'photo002.json').read_bytes()).hexdigest(),'cross_row_results':[]}
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
 r['values']=dict(zip(['gpu_pci_id','pci_command_status','gpu_bar0','crtc25','vpll_coefficient','clock_selection','output_control','packed_crtc39_28_19_13','framebuffer_start','pfb_configuration'],values))
 packed=values[7]
 r['crtc_bytes']={'13':packed&255,'19':(packed>>8)&255,'28':(packed>>16)&255,'39':(packed>>24)&255}
 r['pitch_from_crtc13_19_25']=8*((((packed>>8)&0xe0)<<3)|(packed&255)|((values[3]&0x20)<<6))
 r['pixel_format_low_nibble']=(packed>>16)&15
 r['scope']='Optical evidence;320 bits threshold/offset checked and middle256 bits cross-row checked. Raw observations, not a programming table or proof of480p initialization. CRTC25 is sampled separately and its stride extension is included.'
 r['passed']=True
finally:
 r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 q.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
