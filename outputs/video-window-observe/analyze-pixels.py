"""Analyze preserved observed pixels without changing the failed run verdict."""
import collections,hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];out=k/case;art=out/'artifacts'
assert (out/'audit.json').exists() and not (out/'pixel-analysis.json').exists()
sys.path.insert(0,str(ws/'work/python-packages'));from PIL import Image
from protocol import expected_bytes
source=(art/'source.rgb').read_bytes();rows=[]
for n in range(18):
 expected=expected_bytes(n,source);ep=struct.unpack('<98304I',expected)
 for prefix in ['move','draw']:
  p=art/(prefix+'%02d.rgb'%n);actual=p.read_bytes();ap=struct.unpack('<98304I',actual)
  bad=[i for i,(a,b) in enumerate(zip(ep,ap)) if (a^b)&0xffffff]
  colors=collections.Counter(ap[i]&0xffffff for i in bad)
  bounds=None if not bad else [min(i%384 for i in bad),min(i//384 for i in bad),max(i%384 for i in bad)+1,max(i//384 for i in bad)+1]
  rows.append(dict(index=n,phase=prefix,mismatches=len(bad),bounds=bounds,top_actual_colors=[dict(rgb=hex(c),pixels=count) for c,count in colors.most_common(8)],actual_sha256=hashlib.sha256(actual).hexdigest(),expected_sha256=hashlib.sha256(expected).hexdigest()))
  if n==0:Image.frombytes('RGB',(384,256),actual,'raw','BGRX').save(art/(prefix+'00.png'))
 if n==0:Image.frombytes('RGB',(384,256),expected,'raw','BGRX').save(art/'expected00.png')
r=dict(rows=rows,verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),physical_access=False,no_gate_waiver=True)
(out/'pixel-analysis.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(rows[:2],indent=2))
