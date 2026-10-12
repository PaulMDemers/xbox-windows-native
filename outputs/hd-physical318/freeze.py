from pathlib import Path
import hashlib,json,ast
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'frozen.json';assert not dest.exists()
assert json.loads((k/'preflight001.json').read_text())['passed']
files=list(k.glob('*.py'))+[k/n for n in ['package.json','capture001.json','preflight001.json','rollback-tests001.json']]
files+=list((k/'artifacts/payload').glob('*'))+list((k/'artifacts/before001').rglob('*'))
files+=[k.parent/'demo-audio-level256'/n for n in ['common001.py','providers001.json','capture002.json']]
files+=[k.parent/'demo-physical253'/n for n in ['accepted-state.json','combined001/collection.json','package.json']]
files+=[k.parent/'hd-windows317'/n for n in ['final-review.json','candidate001/combined-review.json','candidate001/fixture.json']]
for folder in ['video-text-oracle206','native-windows-fatx-preflight']:
 files+=list((k.parent/folder).glob('*.py'))
files+=[k.parent/'native-windows-fatx-preflight/artifacts/default.xbe',k.parent/'native-windows-physical-f/decode-legacy-events.py',k.parent/'surface-bridge260/atomic_json.py']
files+=list((k.parent/'hd-interlace316').glob('*.json'))+list((k.parent/'hd-interlace316').glob('*.c'))+list((k.parent/'hd-interlace316').glob('*.h'))
pins={}
for p in files:
 if not p.is_file():continue
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 pins[str(p.resolve())]=hashlib.sha256(p.read_bytes()).hexdigest()
dest.write_text(json.dumps(pins,indent=2)+'\n');print('Frozen',len(pins),'physical318 source/payload/captured rollback files')
