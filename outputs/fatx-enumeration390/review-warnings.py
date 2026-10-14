import json,re,hashlib
from pathlib import Path
base=Path('/home/paul/xbox-windows-native/build')
a=(base/'fatx-directory-order-001/build.log').read_bytes();b=(base/'fatx-enumeration390-001/build.log').read_bytes()
def warnings(raw):
 lines=raw.decode('utf-8','replace').splitlines()
 return [re.sub(r'/home/paul/xbox-windows-native/build/[^/]+/', '<build>/',s) for s in lines if 'warning:' in s]
x,y=warnings(a),warnings(b)
r=dict(parent_log_sha256=hashlib.sha256(a).hexdigest(),candidate_log_sha256=hashlib.sha256(b).hexdigest(),parent_warnings=x,candidate_warnings=y,new_warning_messages=sorted(set(y)-set(x)),passed=not(set(y)-set(x)))
p=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/fatx-enumeration390/warning-review.json');assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'parent_count':len(x),'candidate_count':len(y),'new_count':len(r['new_warning_messages'])}))
