"""Independent stricter host review: counters cannot reset in gaps between steps."""
from upload_analysis import analyze,packet,FIELDS
def review(log,enabled):
 r=analyze(log,enabled)
 if not r['passed']:return r
 try:
  rows=[v.split() for v in log.splitlines() if v.startswith('UPLOAD_WORD_tag_index_value ')]
  snapshots=[packet([int(v[3]) for v in rows[t*158:(t+1)*158]],enabled) for t in range(160)]
  for before,after in zip(snapshots,snapshots[1:]):
   assert all(after[k][f]>=before[k][f] for k in range(15) for f in FIELDS),'Counter decreased across an interval or inter-step gap'
  r['all_159_snapshot_transitions_monotonic']=True
 except (AssertionError,ValueError,IndexError,KeyError) as e:r.update(passed=False,error=repr(e))
 return r
