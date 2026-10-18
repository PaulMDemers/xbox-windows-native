"""Compare closed success/failure preparation records; do not launch anything."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;rows=[]
for case,kind in [(478,'texture'),(481,'depth'),(482,'depth')]:
 kit=K.parent/f'd3d-{kind}{case}'
 c=json.loads((kit/'physical001-collection.json').read_text());p=Path(c['files'][f'/E/Applications/XWNBoot{case}a/report.bin']['path']);raw=p.read_bytes();v=list(struct.unpack('<44I',raw))
 # Only explicit magic/cookie fields are normalized; every other word retained.
 for i in (0,3,42):v[i]=0
 rows.append(dict(case=case,path=str(p),sha256=hashlib.sha256(raw).hexdigest(),normalized=v,Windows_receipts_observed=bool(c.get('result_directory'))))
base=rows[0]['normalized']
for r in rows:r['differences_from_success478']=[dict(word=i,success=a,observed=b) for i,(a,b) in enumerate(zip(base,r['normalized'])) if a!=b]
src=Path('C:/xwn482/build001/xbeboot.S');s=src.read_text();symbols={}
for name in ['diag_handoff','diag_marker_ready','blentry','newloc']:
 for line in Path('C:/xwn482/build001/symbols.txt').read_text().splitlines():
  p=line.split()
  if len(p)==3 and p[2]==name:symbols[name]=int(p[0],16)
record=dict(read_only=True,physical_launches=0,rows=rows,source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),source_path=str(src),symbols=symbols,
 observation_gap=['final trailer flush','NtClose','post-I/O payload and both loader comparisons','second bounded SMBus marker','restored register/flag state and jump','paging-off instruction fetch and GDT/segment transition','payload entry and Windows bootstrap'],
 conclusion='Preparation fields alone do not distinguish successful478 from failed481/482; absence of refusal is not proof these later steps succeeded.',
 next_design='Review an owned bounded observable marker at the first still-unproved boundary; keep final I/O outside privileged transition, preserve register/flag state and both loader copies, host-test failures before any new build/boot. No new diagnostic installed.')
assert 'call diag_flush' in s and 'diag_marker_ready:' in s
(K/'closed-handoff-review001.json').write_text(json.dumps(record,indent=2)+'\n');print([(r['case'],r['differences_from_success478']) for r in rows])
