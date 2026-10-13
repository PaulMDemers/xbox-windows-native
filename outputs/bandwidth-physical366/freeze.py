import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'frozen.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(K/'host004.json')['passed']
assert read(K.parent/'bandwidth-runtime365/final-review.json')['scoped_combined_passed']
old=read(K.parent/'eligible-physical353/frozen.json');paths=[W/n for n in old]
paths+=list(K.glob('*.py'))+[K/'package.json',K/'host004.json',K/'source-review004.json']
oldemu=read(K.parent/'bandwidth-runtime365/candidate001/emulator-frozen.json')
paths+=[W/n for n in oldemu]
paths+=[K.parent/'bandwidth-runtime365'/n for n in ['candidate001/audit.json','candidate001/closure.json','final-review.json']]
paths+=[K.parent/'bandwidth-runtime365'/n for n in ['joined_identity.py','joined_review.py','candidate001/joined-review.json']]
pins={}
for p in paths:
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 pins[p.relative_to(W).as_posix()]=sha(p)
for n,h in old.items():assert pins[n]==h,n
for n,h in oldemu.items():assert pins[n]==h,n
dest.write_text(json.dumps(pins,indent=2)+'\n');print(len(pins),'356 frozen inputs')
