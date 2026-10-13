import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'frozen.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(K/'host001.json')['passed']
old=read(K.parent/'hd-phase-physical347/frozen.json');paths=[W/n for n in old if not n.startswith('outputs/hd-phase-physical347/')]
paths+=list(K.glob('*.py'))+[K/'package.json',K/'host001.json']
for folder in ['eligible-copy351','eligible-runtime352']:
 paths+=list((K.parent/folder).glob('*.py'))
paths+=[K.parent/'eligible-copy351'/n for n in ['build001.json','binary-review001.json','source-review001.json','host001.json','probe/build001.json','probe/build-review001.json']]
paths+=[K.parent/'eligible-runtime352'/n for n in ['parser001.json','protocol001.json','control001/audit.json','candidate001/audit.json','final-review.json']]
pins={}
for p in paths:
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 pins[p.relative_to(W).as_posix()]=sha(p)
dest.write_text(json.dumps(pins,indent=2)+'\n')
(K/'postflight-tools.json').write_text(json.dumps(dict(source_sha256={n:sha(K/n) for n in ['review-pair.py','final-state.py']}),indent=2)+'\n');print(len(pins),'353 frozen inputs')
