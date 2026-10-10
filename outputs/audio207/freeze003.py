import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'frozen003.json').exists()
pins=json.loads((k/'frozen002.json').read_text());assert all(sha(repo/n)==h for n,h in pins.items())
for name in ['Run003.ps1','supervise003.py','audit003.py','typed-state003.py','prepare-fixture002.py','candidate002/fixture.json','0208-fixed-codec-cumulative.patch','build-review002.json','source-build002.json','host-tests003.json','codec-tests002.json','artifacts/build002/ac97xnt5.sys']:
    pins[str((k/name).relative_to(repo)).replace('\\','/')]=sha(k/name)
(k/'frozen003.json').write_text(json.dumps(pins,indent=2)+'\n')
print('Froze candidate002 inputs; no guest launched')
