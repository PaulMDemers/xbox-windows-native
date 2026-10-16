"""Compare fresh canonical-path outputs with exact live415 bytes."""
import hashlib
import json
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'outputs/baseline-compare415'))
from compare import pe_compare
sha=lambda b:hashlib.sha256(b).hexdigest()
r=json.loads((K/'build001.json').read_text());assert r['status']=='compiled'
rows=[]
for profile,artifact,remote,base in [
    ('hal','halxboxnt5.dll','Applications/XWNEBoot/loader/halxboxnt5.dll',0),
    ('loader','freeldr.sys','Applications/XWNEBoot/freeldr.sys',2048),
    ('loader','rosload.exe','Applications/XWNEBoot/rosload.exe',0)]:
    old=(Path('/mnt/e/xwn415/demo')/remote).read_bytes()
    new=(Path(r['cases'][profile]['output'])/'artifacts'/artifact).read_bytes()
    expected=next(a for a in r['cases'][profile]['result']['artifacts'] if a['file']==artifact)
    assert sha(new)==expected['sha256']
    live=json.loads((W/'outputs/baseline-compare415/physical001.json').read_text())
    assert sha(old)==live['files']['/E/'+remote]['sha256']
    details=pe_compare(old,new,base)
    rows.append(dict(file=artifact,demo_sha256=sha(old),rebuilt_sha256=sha(new),
                     source_profile=profile,details=details,
                     prepended_stub_exact=old[:base]==new[:base]))
result=dict(files=rows,all_nonmetadata_bytes_exact=all(x['details']['timestamp_checksum_only'] for x in rows),
            physical_access=False,guest_launch=False,scope='Complete-file byte correspondence, not runtime qualification')
with (K/'comparison001.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
