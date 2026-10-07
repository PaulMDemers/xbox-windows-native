"""Create a fresh successful-map diagnostic; never touch completed cases."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'dump-fsctl-trace';new=k.parent/'fatx-dump-map'
names=['probe.c','Build.ps1','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','configuration.py','check-oracle.py','review.py','record-closure.py','verify-evidence.py','atomic_json.py','trace.py']
for name in names:
    p=k/name;assert not p.exists();s=(old/name).read_text().replace('dump-fsctl-trace','dump-map-trace').replace('xwndf01','xwndt01')
    if name=='prepare.py':
        s=s.replace("assert sha(hal)==hal_record['sha256']", "assert sha(hal)==hal_record['sha256']\nfatx_record=read(k/'fatx-review.json')['candidate001'];fatx=k/'artifacts'/fatx_record['name'];assert sha(fatx)==fatx_record['sha256']")
        assert s.count('w.flush()')==1
        s=s.replace('w.flush()',"fatx_row=next(v for v in protected if v['volume']=='F' and v['path']=='winnt/system32/drivers/xwnfatx.sys')\nfatx_before=fatx_row['sha256'];m.replace(w,fatx_row['path'],fatx.read_bytes());fatx_row['sha256']=sha(fatx)\nw.flush()")
        s=s.replace('hal_before_sha256=hal_before,',"fatx_review_sha256=sha(k/'fatx-review.json'),fatx_before_sha256=fatx_before,fatx_after_sha256=sha(fatx),hal_before_sha256=hal_before,")
        s=s.replace('Only rebuilt HAL and helper payloads differ; FATX0101/video0093 unchanged.','Candidate0102 HAL and0103 FATX installed in owned child only; video0093 unchanged.')
    if name=='preflight.py':
        s=s.replace("assert sha(k/'hal-review.json')", "assert sha(k/'fatx-review.json')==f['fatx_review_sha256']\nassert sha(k/'hal-review.json')")
        s=s.replace("paths+=['hal-review.json',", "paths+=['fatx-review.json','cold-map.py','hal-review.json',")
    if name=='audit.py':s=s.replace('candidate0102 HAL and unchanged FATX0101/video0093','candidate0102 HAL/FATX0103 and unchanged video0093')
    p.write_text(s)
for name in ['hal-review.json','fatx-review.json']:(k/name).write_bytes((new/name).read_bytes())
(k/'layouts.json').write_bytes((old/'layouts.json').read_bytes())
s=(new/'cold-map.py').read_text().replace('fatx-dump-map','dump-map-trace').replace("['control001','candidate001']","['trace001']")
(k/'cold-map.py').write_text(s)
(k/'artifacts').mkdir(exist_ok=True)
for name,p in [('hal-candidate001.dll',k.parent/'hal-dump-path/artifacts/hal-candidate001.dll'),('fatx-candidate001.sys',new/'artifacts/fatx-candidate001.sys')]:
    (k/'artifacts'/name).write_bytes(p.read_bytes())
print('New scripts created; no fixture/guest launched')
