"""Read actual event-message providers from the immutable stop001 source fixture."""
import json, os, sys
from pathlib import Path
sys.dont_write_bytecode = True
k = Path(__file__).resolve().parent
repo = k.parents[2]
assert os.environ.get('XWN_BUILD_LEASE') == 'held'
sys.path.insert(0, str(repo / 'outputs/setup-wizard-automation201'))
from common import ColdIO, readers, sha, read, save
sys.path.insert(0, str(k.parent))
from inventory import snapshot
old = k.parent / 'stop001/candidate001'
fixture = read(old / 'fixture.json')
source = old / 'artifacts/source.qcow2'
assert sha(source) == fixture['source_sha256'] == 'a4c256958b4de6f4347cd657eec013389872a6c4f1fbf86addc1c7a95d215616'
dest = k / 'artifacts/providers001'
assert not dest.exists()
dest.mkdir(parents=True)
values = snapshot(old / 'artifacts/before-system')
rows = []
with ColdIO(source) as io:
    rr = readers(io, source)
    for name in ('Kbdclass', 'Mouclass', 'Dhcp'):
        key = next(p for p in values if p.lower() == '\\controlset001\\services\\eventlog\\system\\' + name.lower())
        row = dict(source=name, registry_key=key, registry_values=values[key], providers=[])
        for raw in values[key]['EventMessageFile']['decoded'].split(';'):
            path = raw.replace('%SystemRoot%', 'winnt').replace('\\SystemRoot', 'winnt').replace('\\', '/')
            if path.lower().startswith('c:/'): path = path[3:]
            data = rr['F'].read(path)
            p = dest / Path(path).name
            if p.exists(): assert p.read_bytes() == data
            else: p.write_bytes(data)
            row['providers'].append(dict(path=path, file=p.name, sha256=sha(p)))
        rows.append(row)
assert sha(source) == fixture['source_sha256']
save(k / 'providers001.json', dict(physical_access=False, source_sha256=fixture['source_sha256'], providers=rows))
print(json.dumps(rows, indent=2))
