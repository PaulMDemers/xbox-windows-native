# SPDX-License-Identifier: MIT
"""Read-only storage plan with actual recorded file identity and allocation."""
import datetime,json,shutil,traceback
from pathlib import Path
from common003 import K,COMPACT,MINIMUM,PROJECTED,sha,volume,processes,selection
OUT=K/'plan003.json';assert not OUT.exists()
r=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,mutated_files=[])
try:
    r['volume']=volume();r['processes']=processes();rows,records=selection()
    assert all(not row['metadata']['attributes']&0x800 for row in rows)
    capacity={d:shutil.disk_usage(d+':/').free for d in ['C','E']}
    r.update(passed=True,files=rows,records=records,compact_path=str(COMPACT),compact_sha256=sha(COMPACT),capacity_free_bytes=capacity,minimum_bytes=MINIMUM,projected_bytes=PROJECTED,guard_before=capacity['C']-PROJECTED>=MINIMUM,logical_bytes=sum(v['metadata']['bytes'] for v in rows),allocated_bytes=sum(v['metadata']['allocated_bytes'] for v in rows),sources={str(p.resolve()):sha(p) for p in [K/'plan003.py',K/'common003.py',K/'DESIGN003.md',K/'.gitattributes']})
except Exception:r['failure']=traceback.format_exc()
finally:
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','logical_bytes','allocated_bytes','guard_before'] if n in r}))
if not r['passed']:raise SystemExit(1)
