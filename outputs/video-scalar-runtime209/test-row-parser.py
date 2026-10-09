"""Reject damaged115 row coverage from actual closed209 logs; no guest mutations."""
import hashlib,json
from pathlib import Path
from dib_analysis import analyze
k=Path(__file__).resolve().parent;dest=k/'row-parser-tests.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=0;inputs={}
for case,mode in [('control001',0),('candidate001',1)]:
 path=k/('emu-'+case)/'artifacts/sample0/gdi-baseline.txt';log=path.read_text(encoding='ascii')
 inputs[str(path.relative_to(k))]=sha(path);assert analyze(log,mode)['passed'];checks+=1
 assert not analyze(log,1-mode)['passed'];checks+=1
 rows=log.splitlines()
 for index,value in [(0,0),(1,114),(2,127),(3,2),(11,1)]:
  hits=[i for i,v in enumerate(rows) if v.split()[:3]==['DIB_AFTER_tag_index_value','10',str(index)]]
  assert len(hits)==1;s=list(rows);s[hits[0]]='DIB_AFTER_tag_index_value 10 %d %d'%(index,value)
  assert not analyze('\n'.join(s)+'\n',mode)['passed'];checks+=1
 s=[v for v in rows if not v.startswith('DIB_AFTER_tag_index_value 10 0 ')]
 assert not analyze('\n'.join(s)+'\n',mode)['passed'];checks+=1
 if mode:
  # Plausible monotonic counters with no new fast work must fail coverage.
  before={int(v.split()[2]):v.split()[3] for v in rows if v.startswith('DIB_BEFORE_tag_index_value 0 ')}
  s=[]
  for v in rows:
   parts=v.split()
   if parts[:2]==['DIB_AFTER_tag_index_value','0'] and 4<=int(parts[2])<=10:parts[3]=before[int(parts[2])];v=' '.join(parts)
   s.append(v)
  assert not analyze('\n'.join(s)+'\n',mode)['passed'];checks+=1
  s=[v for v in rows if not v.startswith('TIMING_kind_count_ms 0 ')]
  assert not analyze('\n'.join(s)+'\n',mode)['passed'];checks+=1
r=dict(passed=True,checks=checks,host_only=True,guest_changes=False,physical_access=False,
 source_pins={p.name:sha(p) for p in [Path(__file__),k/'dib_analysis.py']},input_pins=inputs,
 limits='Negative mutations of actual closed row ABI/coverage logs only; does not substitute for runtime pixels or cold integrity.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Actual115 ABI/coverage rejection checks:',checks)
