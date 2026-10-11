import pathlib,json,hashlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k/'frozen005.json').read_text());assert all(sha(repo/n)==v for n,v in pins.items())
assert json.loads((k/'candidate004/audit.json').read_text())['scoped_audio_passed']
for n in ['Run-Install001.ps1','Wait-Install001.ps1','supervise-install001.py','audit-install001.py','typed-state-install001.py','installed-binding001.py','prepare-install001.py','install001/fixture.json','install.c','install-runner.c','xwnaci207.inf','install-review002.json','artifacts/install001/install.exe','artifacts/install001/install-runner.exe']:
 p=k/n;pins[str(p.relative_to(repo)).replace(chr(92),'/')]=sha(p)
p=k/'frozen-install001.json';assert not p.exists();p.write_text(json.dumps(pins,indent=2)+'\n')
print('Froze genuine installation inputs')
