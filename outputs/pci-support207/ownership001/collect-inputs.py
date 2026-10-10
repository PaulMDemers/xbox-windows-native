"""Read owned cold evidence/source; no console, hive, or source modifications."""
import hashlib
import json
import re
import sys
from pathlib import Path
sys.dont_write_bytecode = True
k = Path(__file__).resolve().parent
pci = k.parent
repo = pci.parents[1]
sys.path.insert(0, str(pci))
from inventory import snapshot
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
out = k / 'inputs.json'
assert not out.exists()
r = dict(scope=__doc__, physical_access=False, fixtures={}, sources={})
physical = read(pci / 'hardware220/physical001.json')['after']['system']
emulator = read(pci / 'hardware220/emulator004/audit.json')
emuhash = next(v['sha256'] for v in emulator['hives'] if v['name'] == 'system')
for name, path, digest in (
    ('physical220', repo / physical['path'], physical['sha256']),
    ('emulator004', pci / 'hardware220/emulator004/artifacts/audit/after-system', emuhash)):
    assert sha(path) == digest
    values = snapshot(path)
    cs = 'ControlSet%03d' % values['\\Select']['Current']['decoded']
    keys = [key for key in values if key.startswith('\\' + cs + '\\Enum\\PCI\\VEN_10DE&DEV_01B4&') and key.endswith('\\LogConf')]
    assert len(keys) == 1
    r['fixtures'][name] = dict(hive_sha256=digest, key=keys[0], values=values[keys[0]])

video = Path('/home/paul/xbox-windows-native/build/video-reuse-001/source/win32ss/drivers/miniport/xboxvmp/nt5')
pins = read(repo / 'outputs/video-trace-reuse/source-review.json')
for pin in pins['unchanged_sources']:
    assert sha(video / Path(pin['path']).name) == pin['sha256']
for file in sorted(video.iterdir()):
    if file.suffix not in ('.c', '.txt'):
        continue
    text = file.read_text()
    r['sources']['video0093/' + file.name] = dict(sha256=sha(file),
        bus_access_lines=[dict(line=i, text=line.strip()) for i, line in enumerate(text.splitlines(), 1)
                          if re.search(r'SMBus|SMB_|READ_PORT|WRITE_PORT|HalGetBusData', line, re.I)])
audio = k.parents[4] / 'audio'
source = audio / 'work/reactos001/drivers/wdm/audio/drivers/ac97'
manifest = read(audio / 'repo/outputs/audio207/source-build004.json')
for name, digest in manifest['sources'].items():
    file = source / name
    assert sha(file) == digest, file
    if file.suffix not in ('.h', '.cpp'):
        continue
    r['sources']['audio004/' + name] = dict(sha256=digest,
        bus_access_lines=[dict(line=i, text=line.strip()) for i, line in enumerate(file.read_text().splitlines(), 1)
                          if re.search(r'SMBus|SMB_|READ_PORT|WRITE_PORT|0xc000|0xc200', line, re.I)])
r['limits'] = 'Audio004 is reviewed candidate source, not provenance for the restored legacy ac97xnt5 binary. Source searches alone do not prove absence of indirect I/O.'
out.write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({name: {n: len(bytes.fromhex(v['hex'])) for n, v in d['values'].items()} for name,d in r['fixtures'].items()}, indent=2))
