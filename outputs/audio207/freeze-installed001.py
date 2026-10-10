import pathlib,json,hashlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((k/'frozen-install001.json').read_text());assert all(sha(repo/n)==v for n,v in pins.items())
assert json.loads((k/'install001/audit.json').read_text())['scoped_installation_passed']
for n in ['Run-Installed001.ps1','Wait-Installed001.ps1','supervise-installed001.py','audit-installed001.py','typed-state-installed001.py','prepare-installed001.py','installed001/fixture.json','state.c','probe-installed.c','installed-runner.c','state-review001.json','artifacts/state001/state.exe','artifacts/state001/probe-installed.exe','artifacts/state001/installed-runner.exe']:
 p=k/n;pins[str(p.relative_to(repo)).replace(chr(92),'/')]=sha(p)
p=k/'frozen-installed001.json';assert not p.exists();p.write_text(json.dumps(pins,indent=2)+'\n')
print('Froze subsequent installed-driver boot inputs')
