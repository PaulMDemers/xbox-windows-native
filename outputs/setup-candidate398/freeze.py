import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
prior=json.loads((K.parent/'fatx-physical394/frozen.json').read_text())
paths=[W/p for p in prior if not p.startswith('outputs/fatx-physical394/')]
paths += [K/'source-review.json',K.parent/'setup-retry397/final-review.json',K.parent/'setup-retry397/control001/control-analysis.json',K.parent/'fatx-physical394/rollback-host001.json']
paths+=list(K.glob('*.py'))+[K/'commands.cmd',K/'startup.cmd',K/'package.json',K/'DESIGN.md']
paths += [K.parent/'setup-wizard-automation201'/n for n in ['wizard006.c','policy.h','build006.json','build-review006.json']]
pkg=json.loads((K/'package.json').read_text())
for v in pkg['helpers']:
 b=Path(v['source']).read_bytes();assert len(b)==v['bytes'] and sha(b)==v['sha256']
 assert all(0<len(part)<=42 and part not in ['.','..'] for part in v['name'].split('/'))
assert pkg['candidate']['sha256']=='41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126'
assert sha(Path(pkg['candidate']['source']).read_bytes())==pkg['candidate']['sha256']
assert (K/'commands.cmd').read_text().replace('C:\\xwndemo398candidate001\\cmd','C:\\xwncmd393')==(K.parent/'cmd-regression393/commands.cmd').read_text()
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
print('Setup-first candidate: validated all payloads, ordering and',len(pins),'frozen inputs')
