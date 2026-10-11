"""Freeze unchanged driver/harness dependencies and exact new helper/fixture inputs."""
import hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1];old=k.parent/'audio207'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=json.loads((old/'frozen-installed002.json').read_text())
assert all(sha(repo/n)==v for n,v in pins.items())
assert json.loads((k/'build002.json').read_text())['passed']
files=[p for p in k.iterdir() if p.is_file() and p.suffix in ['.py','.ps1','.c','.h','.md','.json']]
files += [k/'artifacts/build002/probe.exe',k/'emu001/fixture.json']
for p in files:pins[p.relative_to(repo).as_posix()]=sha(p)
with (k/'frozen.json').open('x') as f:json.dump(pins,f,indent=2)
print('Frozen inputs:',len(pins))
