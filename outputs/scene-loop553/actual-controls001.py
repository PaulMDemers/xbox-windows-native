"""Reject malformed copies of actual telemetry without editing guest evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];sys.path.insert(0,str(W/'tools'))
import graphics_sceneloop as scene
r=json.loads((K/'runtime-review002.json').read_text());assert r['all_allowed_cases_passed']
out=K/'actual-controls001.json';assert not out.exists();rows=[]
for row in r['rows']:
 f=row['fields'];count=0
 for key in f:
  if not key.startswith('loop.'):continue
  for remove in (False,True):
   bad=dict(f)
   if remove:del bad[key]
   else:bad[key]='invalid'
   try:scene.telemetry(bad)
   except ValueError:count+=1
   else:raise AssertionError(key)
 rows.append(dict(name=row['name'],rejections=count))
out.write_text(json.dumps(dict(passed=True,rows=rows,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n');print(rows)
