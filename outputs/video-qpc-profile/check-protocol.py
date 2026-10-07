"""Reject corrupted timing evidence using real closed-run logs; never operate guests."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
source=(k/'common.py').read_text();node=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='validate_log')
ns={};exec(compile(ast.Module(body=[node],type_ignores=[]),str(k/'common.py'),'exec'),ns)
validate=ns['validate_log'];checks=[]
for case in ['control001','instrumented001']:
 data=(k/case/'artifacts/result.log').read_bytes();assert validate(data)['passed'];checks.append(case+': original accepted')
 def reject(name,mutate):
  rows=data.decode('ascii').splitlines();mutate(rows);result=validate(('\n'.join(rows)+'\n').encode('ascii'));assert not result['passed'],name;checks.append(case+': '+name+' rejected')
 def replace(rows,label,value):
  index=next(i for i,s in enumerate(rows) if s.startswith(label+' '));rows[index]=label+' '+value
 reject('zero frequency',lambda r:replace(r,'QPC_FREQUENCY','0 0 0'))
 reject('word outside DWORD',lambda r:replace(r,'QPC_OUTER','0 4294967296 1'))
 reject('negative interval word',lambda r:replace(r,'QPC_OUTER','0 -1 1'))
 reject('invalid mode',lambda r:replace(r,'QPC_MODE','2 0 0'))
 reject('premature loop',lambda r:replace(r,'TIMING_COUNT_MS_PIXELS','1 1 4096'))
 reject('component exceeds outer',lambda r:replace(r,'QPC_OPERATION','2147483647 0 '+next(s for s in r if s.startswith('QPC_OPERATION ')).split()[3]))
 reject('calibration range inconsistent',lambda r:replace(r,'QPC_CAL_PRE_RANGE','4294967295 4294967295 128'))
 reject('missing counter record',lambda r:r.pop(next(i for i,s in enumerate(r) if s.startswith('QPC_FLUSH '))))
 reject('missing completion',lambda r:r.pop(next(i for i,s in enumerate(r) if s.startswith('COMPLETE '))))
 reject('coarse clock disagrees',lambda r:replace(r,'TIMING_COUNT_MS_PIXELS',next(s for s in r if s.startswith('TIMING_COUNT_MS_PIXELS ')).split()[1]+' 29999 4096'))
p=k/'protocol-check.json';assert not p.exists();p.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=hashlib.sha256(source.encode()).hexdigest(),check_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print('Real logs accepted and '+str(len(checks)-2)+' damaged protocols rejected')
