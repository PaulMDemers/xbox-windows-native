import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'frozen004.json').exists()
pins=json.loads((k/'frozen003.json').read_text());assert all(sha(repo/n)==h for n,h in pins.items())
for name in ['Run004.ps1','Invoke-Audio004.ps1','supervise004.py','audit004.py','typed-state004.py','prepare-fixture003.py','candidate003/fixture.json','0209-render-connections-cumulative.patch','build-review003.json','source-build003.json','connection-tests004.json','artifacts/build003/ac97xnt5.sys']:
    pins[str((k/name).relative_to(repo)).replace('\\','/')]=sha(k/name)
(k/'frozen004.json').write_text(json.dumps(pins,indent=2)+'\n');print('Froze candidate003 inputs; no guest launched')
