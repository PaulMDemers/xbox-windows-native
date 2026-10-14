import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
prior=json.loads((K.parent/'fatx-physical394/frozen.json').read_text())
paths=[W/p for p in prior if not p.startswith('outputs/fatx-physical394/')]
paths+=list(K.glob('*.py'))+[K/'commands.cmd',K/'startup.cmd',K/'package.json',K/'DESIGN.md']
paths += [K.parent/'setup-wizard-automation201'/n for n in ['wizard006.c','policy.h','build006.json','build-review006.json']]
pkg=json.loads((K/'package.json').read_text())
for v in pkg['helpers']:
 b=Path(v['source']).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256']
 assert all(0<len(part)<=42 and part not in ['.','..'] for part in v['name'].split('/'))
assert pkg['candidate']['sha256']=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
assert sha(Path(pkg['candidate']['source']).read_bytes())==pkg['candidate']['sha256']
assert (K/'commands.cmd').read_text().replace('C:\\xwndemo397control001\\cmd','C:\\xwncmd393')==(K.parent/'cmd-regression393/commands.cmd').read_text()
s=(K/'startup.cmd').read_text()
order=['gate\\wizard.exe /cancel-physical','if not "%XWN_GATE_RC%"=="0" goto blocked','\\file-probe.exe','\\cmd.exe /d /c','\\runner.exe /physical']
positions=[s.index(v) for v in order];assert positions==sorted(positions)
assert s.count('gate\\wizard.exe /cancel-physical')==1
pins={}
for p in paths:
 b=p.read_bytes()
 if p.suffix=='.py':ast.parse(b)
 pins[p.relative_to(W).as_posix()]=sha(b)
dest=K/'frozen.json';assert not dest.exists();dest.write_text(json.dumps(pins,indent=2)+'\n')
print('Setup-first original control: validated all payloads, ordering and',len(pins),'frozen inputs')
