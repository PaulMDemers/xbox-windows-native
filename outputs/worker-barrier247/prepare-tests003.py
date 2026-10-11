"""Retain adapter002 failure; correct successful-mode expectation only."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;assert not (k/'test-worker003.py').exists()
assert not json.loads((k/'worker-test002.json').read_text())['passed']
(k/'test-worker003.c').write_text((k/'test-worker002.c').read_text().replace('if(mode<=5||mode==10)','if((mode>=1&&mode<=5)||mode==10)'))
s=(k/'test-worker002.py').read_text().replace('worker-test002','worker-test003').replace("k/'test-worker002.c'","k/'test-worker003.c'")
(k/'test-worker003.py').write_text(s)
(k/'worker-proof001-failure.json').write_text(json.dumps(dict(passed=False,error='Final negative adapter replaced an unmatched timestamp, leaving the positive log unchanged; parser correctly accepted it',source_sha256=hashlib.sha256((k/'test-worker-proof.py').read_bytes()).hexdigest(),guest_launch=False),indent=2)+'\n')
s=(k/'test-worker-proof.py').read_text().replace('import hashlib,json','import hashlib,json,re').replace('worker-proof001.json','worker-proof002.json')
s=s.replace("lines[-1].replace(str(time+220000000),str(time+1000000))","re.sub(r'when=\\d+',f'when={time+1000000}',lines[-1])")
(k/'test-worker-proof002.py').write_text(s)
p=k/'prelaunch-review.py';p.write_text(p.read_text().replace('worker-test002','worker-test003').replace('worker-proof001','worker-proof002'))
print('Fresh adapter003 and proof002, failed evidence retained')
