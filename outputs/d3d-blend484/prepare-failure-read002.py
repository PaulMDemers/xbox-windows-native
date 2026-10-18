"""Prepare a complete module read for failed pixels; preserve successful subset read001."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'independent002.py';assert not p.exists()
s=(K/'independent001.py').read_text().replace('d3d-blend484-independent001','d3d-blend484-independent002').replace("K/'independent001.json'","K/'independent002.json'")
a=s.index("for row in runtime['rows']:");b=s.index('assert 12<len(selected)',a)
s=s[:a]+'''# The original validator reached its pixel check after validating metadata.
# Decode the already captured module fields even though image qualification failed.
sys.path.insert(0,str(W/'tools'));import graphics_blend as g
for row in runtime['rows']:
 assert row['review_failure']=='a0 pixel 8,8' and row['process_exit']==0
 f=row['fields']
 for j in range(g.integer(f['modules'])):
  name=g.unhex(f[f'module{j}.path'],1,259).decode('ascii')
  path=name[3:].replace(chr(92),'/').lower();assert path in manifest
  selected.add(path)
'''+s[b:]
p.write_text(s,encoding='utf-8',newline='\n')
p=K/'module-review002.py';assert not p.exists()
s=(K/'module-review001.py').read_text().replace('module-review001.json','module-review002.json').replace('independent001.json','independent002.json')
s=s.replace("assert r['all_allowed_cases_passed']","assert not r['all_allowed_cases_passed']")
s=s.replace("for j,name in enumerate(case['review']['modules']):","for j in range(int(case['fields']['modules'])):\n  name=bytes.fromhex(case['fields'][f'module{j}.path']).decode('ascii')")
p.write_text(s,encoding='utf-8',newline='\n')
print('New read-only failed-case module audit prepared; no runtime replay.')
