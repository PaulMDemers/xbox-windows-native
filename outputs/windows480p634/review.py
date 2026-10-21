"""Host review of prepared bytes and drawing-oracle discrimination; no VM launch."""
import array,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
b=json.loads((K/'build002.json').read_text());p=json.loads((K/'preparation001.json').read_text());r=json.loads((K/'runtime001.json').read_text())
assert b['compiled'] and not b['warnings'] and p['prepared'] and p['allocation_consistent']
assert not (K/'runner001.json').exists() and not Path('C:/xwn634/emu001/instance.json').exists()
assert sha(K/'probe.c')==b['source_pins']['probe.c']==p['probe_source_sha256']
for group in ['dependencies','parents','initial']:
 for name,h in r[group].items():assert sha(Path(name))==h,name
pe=pefile.PE(b['output_windows']);assert pe.FILE_HEADER.Machine==0x14c
assert (pe.OPTIONAL_HEADER.MajorSubsystemVersion,pe.OPTIONAL_HEADER.MinorSubsystemVersion)==(5,0)
assert sha(Path(b['output_windows']))==b['binary_sha256']
assert p['imports']=={x.dll.decode().lower():[v.name.decode() for v in x.imports] for x in pe.DIRECTORY_ENTRY_IMPORT}
# Independent byte-channel construction and a snapshot-based copy reference.
# This checks the mathematical oracle, not GDI or the compiled guest's execution.
def pixel(x,y):return int.from_bytes(bytes([(x^y^90)%256,(29*y+7*x)%256,(17*x+3*y)%256,0]),'little')
a=array.array('I',(pixel(x,y) for y in range(480) for x in range(720)))
checks=0;negative=0
for sx,sy,dx,dy in [(30,40,47,53),(47,53,30,40)]:
 expected=array.array('I',a)
 for y in range(120):expected[(dy+y)*720+dx:(dy+y)*720+dx+200]=a[(sy+y)*720+sx:(sy+y)*720+sx+200]
 for y in range(480):
  for x in range(720):
   px,py=(x-dx+sx,y-dy+sy) if dx<=x<dx+200 and dy<=y<dy+120 else (x,y)
   assert expected[y*720+x]==pixel(px,py);checks+=1
 assert expected!=a;negative+=1 # omitted copy
 bad=array.array('I',a)
 ys=range(120) if dy>sy else range(119,-1,-1)
 xs=range(200) if dx>sx else range(199,-1,-1)
 for y in ys:
  for x in xs:bad[(dy+y)*720+dx+x]=bad[(sy+y)*720+sx+x]
 assert bad!=expected;negative+=1 # wrong traversal on overlapping copy
 for at in [0,719,720,345599,(dy+60)*720+dx+100]:
  changed=array.array('I',expected);changed[at]^=1;assert changed!=expected;negative+=1
out=dict(passed=True,scope='Prepared-byte/NT5-import review and independent drawing-oracle math; no guest execution',pixel_comparisons=checks,negative_cases_rejected=negative,source_sha256=sha(K/'probe.c'),binary_sha256=b['binary_sha256'],runtime_dependencies_unchanged=True,parents_unchanged=True,never_launched=True,physical_access=False)
(K/'host-review001.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
