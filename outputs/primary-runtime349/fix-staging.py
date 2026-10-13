import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent
assert not (K/'preparation-refusal001.json').exists() and not (K/'control001').exists()
p=K/'prepare.py';old=p.read_bytes();s=old.decode().replace('/home/paul/xbox-windows-native/work/primary349-','/home/paul/xbox-windows-native/build/primary349-staging002-')
assert s!=old.decode();(K/'prepare002.py').write_text(s)
oldps=(K/'Prepare.ps1').read_text();(K/'Prepare002.ps1').write_text(oldps.replace('/prepare.py','/prepare002.py'))
(K/'preparation-refusal001.json').write_text(json.dumps(dict(stage='Before private staging directory, fixture output, disk mutation or guest launch',error='PermissionError creating work/primary349-control001; use existing writable private build root instead',original_source_sha256=hashlib.sha256(old).hexdigest(),corrected_source_sha256=hashlib.sha256((K/'prepare002.py').read_bytes()).hexdigest(),old_source_preserved=True,guest_launched=False,physical_access=False),indent=2)+'\n')
