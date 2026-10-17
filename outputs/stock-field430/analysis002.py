"""Read-only post-analysis of actual records/captures and source timing subset."""
import hashlib,json,re,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn430/physical003')
sys.path.insert(0,str(W/'outputs/field-scanout428'))
from oracle import verify_pixels
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(rows):
 if len(rows)!=10:raise ValueError('count')
 for n,r in enumerate(rows[1:9]):
  mode,phase=divmod(n,4);w,h=(1280,720) if mode==0 else (1920,1080)
  if r[:6]!=[0x430c0de,1,mode,phase,w,h]:raise ValueError('identity')
  if r[10] or r[8]<w*h*4 or r[7]!=r[9] or (r[6]&0x7fffffff)!=r[7]:raise ValueError('framebuffer')
  if r[7]%4096 or r[7]+r[8]>64*1024**2:raise ValueError('RAM')
  if not 1<=r[11]<=250 or not 10000<=r[12]<=30000:raise ValueError('coverage')
  if r[13]!=rows[0][13] or (r[13]&255)!=4:raise ValueError('encoder setting')
  first=rows[1+mode*4]
  if r[6:10]!=first[6:10] or r[16:]!=first[16:]:raise ValueError('changed mode state')
 if rows[0][3]!=99 or rows[-1][2:4]!=[0,100]:raise ValueError('completion')
def main():
 out=K/'analysis002.json';assert not out.exists()
 rec=json.loads((K/'physical003-collection.json').read_text());assert rec['completed']
 for n,v in rec['files'].items():assert sha(P/n)==v['sha256']
 data=(P/'result.bin').read_bytes();rows=[list(struct.unpack('<32I',data[i:i+128])) for i in range(0,len(data),128)]
 check(rows);negative=0
 for i in range(1,9):
  for word in list(range(6))+[6,7,8,9,10,13]:
   mutated=[r.copy() for r in rows];mutated[i][word]^=0x80000000
   try:check(mutated)
   except ValueError:negative+=1
   else:raise AssertionError((i,word))
 pixels=sum(verify_pixels((P/('capture-%d.bgrx'%i)).read_bytes(),i%4) for i in range(8))
 source=W/'src/boot/xromwell/drivers/video/xwn_hd_profile.c';s=source.read_text()
 offsets=[int(x,0) for x in re.search(r'xwn_hd_mmio_offsets\[28\]=\{([^}]+)',s)[1].split(',')]
 profiles=[]
 for line in s.splitlines():
  if line.startswith(' {1280u') or line.startswith(' {1920u'):
   arrays=re.findall(r'\{([^{}]+)\}',line)
   profiles.append([int(x,0) for x in arrays[1].split(',')])
 comparisons=[]
 for mode in range(2):
  row=rows[1+mode*4];observed={0x680800+i*4:v for i,v in enumerate(row[16:])}
  expected=dict(zip(offsets,profiles[mode]));shared=sorted(observed.keys()&expected.keys())
  assert len(shared)==14
  assert all(observed[a]==expected[a] for a in shared)
  comparisons.append(dict(mode=mode,addresses=shared,values=[observed[a] for a in shared]))
 result=dict(passed=True,captures_rehashed=len(rec['files']),pixels_verified=pixels,actual_record_mutations_rejected=negative,framebuffer_physical_matches_scanout=True,timing_subset=comparisons,profile_source_sha256=sha(source),scope='14 stock-runtime registers per mode equal public profile constants. NOT actual Windows runtime register capture, full CRTC/encoder comparison, or external signal validation.',user_observation='on 720 everything looks perfect, on 1080, every other column is a solid color.',photos_received=False,owned_sessions='closed')
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':True,'actual_mutations':negative,'timing_registers_per_mode':14}))
if __name__=='__main__':main()
