import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (k/'frozen005.json').exists()
pins=json.loads((k/'frozen004.json').read_text());assert all(sha(repo/n)==h for n,h in pins.items())
for name in ['Run005.ps1','Invoke-Audio.ps1','supervise005.py','audit005.py','typed-state005.py','prepare-fixture004.py','candidate004/fixture.json','0210-waveonly-cumulative.patch','build-review004.json','source-build004.json','artifacts/build004/ac97xnt5.sys']:
    pins[str((k/name).relative_to(repo)).replace('\\','/')]=sha(k/name)
(k/'frozen005.json').write_text(json.dumps(pins,indent=2)+'\n');print('Froze candidate004 inputs; no guest launched')
