import ast,json,hashlib
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
old=json.loads((K.parent/'demo-validation387/frozen.json').read_text());paths=[W/p.replace('outputs/demo-validation387/','outputs/fatx-physical394/') for p in old if not p.endswith('frozen.json')]
paths+=list(K.glob('*.py'))+[K/'commands.cmd',K/'startup.cmd',K/'package.json',K/'DESIGN.md',K/'rollback-host001.json',K.parent/'fatx-enumeration390/final-review.json',K.parent/'fatx-enumeration390/binary-review.json',K.parent/'cmd-regression393/final-review.json',K.parent/'cmd-regression393/source-review.json']
pkg=json.loads((K/'package.json').read_text())
for row in pkg['helpers']:
 b=Path(row['source']).read_bytes();assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256'];assert all(0<len(v)<=42 and v not in ['.','..'] for v in row['name'].split('/'))
cmd=(K/'commands.cmd').read_text().replace('C:\\xwndemo394candidate001\\cmd','C:\\xwncmd393');assert cmd==(K.parent/'cmd-regression393/commands.cmd').read_text()
s=(K/'startup.cmd').read_text().replace('C:\\xwndemo394candidate001\\cmd','C:\\xwncmd393').replace('C:\\xwndemo394candidate001','C:\\xwnenumeration391').replace('/physical','/emulator');assert s==(K.parent/'cmd-regression393/startup.cmd').read_text()
pins={}
for p in paths:
 b=p.read_bytes()
 if p.suffix=='.py':ast.parse(b.decode('utf-8-sig'))
 pins[p.relative_to(W).as_posix()]=hashlib.sha256(b).hexdigest()
p=K/'frozen.json';assert not p.exists();p.write_text(json.dumps(pins,indent=2)+'\n')
print('Validated payloads/command source and froze',len(pins),'inputs')
