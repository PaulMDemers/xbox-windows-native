"""Review a controller-only receipt correction; no hardware or runtime access."""
from pathlib import Path
import json,hashlib,re
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
old=(K/'physical005.py').read_text()
new=(K/'physical006.py').read_text()
assert new==old.replace("'plan-review002.json'","'plan-review001.json'").replace("'review002.json'","'review003.json'").replace("'sources002.json'","'sources003.json'")
assert "['plan-review001.json','page-review002.json','review003.json']" in new
for name,want in read(K/'sources002.json')['files'].items():assert sha(K/name)==want,name
for name,want in read(K/'review002.json')['checks'].items():assert sha(K/name)==want,name
for name in ['plan-review001.json','page-review002.json','review002.json']:assert read(K/name)['passed']
r={'passed':True,'physical_access':False,'old_controller_sha256':sha(K/'physical005.py'),'new_controller_sha256':sha(K/'physical006.py'),'old_frozen_sources_exact':True,'old_qualification_receipts_exact':True,'changes':['correct plan receipt to existing passed001','new freeze review003/sources003'],'production_inputs_changed':False,'launch_logic_changed':False}
out=K/'controller-review001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
print('PASS controller-only receipt correction; prior qualification and sources unchanged')
