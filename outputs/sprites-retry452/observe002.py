"""Bounded read-only dashboard-return observation; never retry a launch."""
import json,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent
sys.path.insert(0,str(K.parent/'field-scanout428'))
from physical import connect,get,utc,write_json
RESULT='/E/xwn452'
out=K/'physical001-observation.json';assert not out.exists()
assert json.loads((K/'physical001-launch.json').read_text())['requested']
r=dict(started_utc=utc(),closed=False,returned=False,attempts=[])
write_json(out,r);start=time.monotonic()
try:
 while time.monotonic()-start<480:
  row=dict(utc=utc(),seconds=round(time.monotonic()-start,2))
  try:
   with connect(timeout=5) as f:
    data=get(f,RESULT+'/runner.txt',True)
    row.update(dashboard=True,runner_present=data is not None)
    # A returned new receipt distinguishes this from a still-live launch connection.
    if data is not None:
     row['runner_bytes']=len(data);r['returned']=True
  except Exception as e:row['error_type']=type(e).__name__
  r['attempts'].append(row);write_json(out,r)
  if r['returned']:break
  time.sleep(10)
finally:
 r.update(closed=True,ended_utc=utc(),deadline=not r['returned']);write_json(out,r)
print(json.dumps({k:r[k] for k in ['returned','closed','deadline']}))
