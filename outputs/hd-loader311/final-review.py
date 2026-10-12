"""Rehash all private host/build evidence and preserve the two host revisions."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
count=0
for n in ['host001.json','host002.json']:
 h=read(k/n);assert h['passed']
 for p,v in h['private_files'].items():assert sha(Path(p))==v,p;count+=1
b=read(k/'build001.json');review=read(k/'binary-review001.json');assert b['status']=='compiled' and review['passed']
for case,row in b['cases'].items():
 for n,v in row['files'].items():assert sha(Path('D:/xwn311/build001')/case/n)==v['sha256'];count+=1
for n,h in b['logs'].items():assert sha(Path('D:/xwn311/build001')/n)==h;count+=1
sources={p.name:sha(p) for p in (k/'integrated').iterdir()}
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,private_files_verified=count,compiled_only=True,physical_access=False,guest_launch=False,host002_checks=read(k/'host002.json')['checks'],control_text_byte_identical_300=review['control_text_byte_identical_300'],matched_warning_instances=review['rows']['candidate001']['warnings'],candidate_sha256=b['cases']['candidate001']['files']['default.xbe']['sha256'],control_sha256=b['cases']['control001']['files']['default.xbe']['sha256'],integrated_sources=sources,limitations='No native hardware/runtime qualification.312 supplies separate ordinary emulator results. Only720p enabled;0.2.0 untagged.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
