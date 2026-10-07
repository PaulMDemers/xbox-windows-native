"""Correct the unlaunched five-thread probe; preserve its initial build metadata."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent
assert not (k/'fixture-001.json').exists()
archive=k/'artifacts/before-waitall-correction';archive.mkdir(exist_ok=False)
for name in ['probe.c','probe-review.json','probe-symbols.json']:
    shutil.copyfile(k/name,archive/name)
shutil.copyfile(k/'artifacts/probe.exe',archive/'probe.exe')
p=k/'probe.c';s=p.read_text();old='if(status!=WAIT_OBJECT_0){report("HELD_FOR_DIAGNOSIS"';assert s.count(old)==1
p.write_text(s.replace(old,'if(status>=WAIT_OBJECT_0+5){report("HELD_FOR_DIAGNOSIS"'))
p=k/'prepare-probe.py';s=p.read_text();marker="target=k/'probe.c';"
assert s.count(marker)==1
s=s.replace(marker,"source=source.replace('if(status!=WAIT_OBJECT_0){report(\"HELD_FOR_DIAGNOSIS\"','if(status>=WAIT_OBJECT_0+5){report(\"HELD_FOR_DIAGNOSIS\"')\n"+marker)
p.write_text(s)
p=k/'audit.py';s=p.read_text();assert r'WAIT_RESULT 0 ([0-9]+)' in s;p.write_text(s.replace(r'WAIT_RESULT 0 ([0-9]+)',r'WAIT_RESULT [0-4] ([0-9]+)'))
r=json.loads((k.parent/'fatx-cleanup-repeat/waitall-correction.json').read_text());r['scope']=__doc__;r['correction']='Accept documented wait-all range0..4 for five thread handles. No change to pending-install guard. Original build never launched.'
(k/'waitall-correction.json').write_text(json.dumps(r,indent=2)+'\n')
