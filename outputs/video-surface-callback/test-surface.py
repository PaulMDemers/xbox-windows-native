"""Synthetic parser and range attribution checks; not guest evidence."""
import importlib.util,json,hashlib
from pathlib import Path
from surface_trace import decode,MAX_SEGMENT
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('verify_surface',k/'verify-surface.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
data=b'nv2a_pgraph_surface_cpu_write 0x03c00000+0xa0000\nnv2a_pgraph_surface_cpu_read 0x00010000+0x4\n'
events=decode(data);assert events==[('write',0x3c00000,0xa0000),('read',0x10000,4)]
sample={side:dict(rows=[dict(points=[dict(physical=base),dict(physical=base+767)])]) for side,base in [('source',0x10000),('destination',0x3ca0000)]}
r=v.correlate(events,sample);assert r['events']==2 and {x['side'] for x in r['addresses']}=={'source','destination'}
checks=2
for data in [b'nv2a_pgraph_surface_cpu_write bad\n',b'nv2a_pgraph_surface_cpu_write 0x03ffffff+0x1\n',b'x'*(MAX_SEGMENT+1)]:
 try:decode(data)
 except AssertionError:checks+=1
 else:raise AssertionError('Bad trace accepted')
assert v.correlate([('read',0,4)],sample)['addresses'][0]['side']=='other';checks+=1
r=dict(passed=True,synthetic_only=True,checks=checks,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['surface_trace.py','verify-surface.py','test-surface.py']})
(k/'surface-tests.json').write_text(json.dumps(r,indent=2)+'\n');print(checks,'surface parser/range checks passed')
