"""Prepare a unique matched ordinary comparison; never launch a guest."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'hal-dump-path'
assert not (k/'control001').exists() and not (k/'candidate001').exists(), 'Never overwrite frozen runtime scripts'
files=['probe.c','Build.ps1','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','configuration.py','check-oracle.py','review.py','record-closure.py','verify-evidence.py','atomic_json.py']
for name in files:
    p=k/name;s=(old/name).read_text().replace('hal-dump-path','fatx-dump-map').replace('xwnhd01','xwndm01')
    if name=='prepare.py':
        s=s.replace("hal_record=hal_review[case]","hal_record=hal_review['candidate001']")
        s=s.replace("hal=k/'artifacts'/hal_record['name']","hal=old_hal=k.parent/'hal-dump-path/artifacts'/hal_record['name']")
        s=s.replace("assert sha(hal)==hal_record['sha256']","assert sha(hal)==hal_record['sha256']\nfatx_record=read(k/'fatx-review.json')[case];fatx=k/'artifacts'/fatx_record['name'];assert sha(fatx)==fatx_record['sha256']")
        assert s.count("w.flush()\ne=m.Writer")==1
        s=s.replace("w.flush()\ne=m.Writer", "fatx_row=next(row for row in protected if row['volume']=='F' and row['path']=='winnt/system32/drivers/xwnfatx.sys')\nfatx_before=fatx_row['sha256'];m.replace(w,fatx_row['path'],fatx.read_bytes());fatx_row['sha256']=sha(fatx)\nw.flush()\ne=m.Writer")
        s=s.replace("hal_before_sha256=hal_before,", "fatx_review_sha256=sha(k/'fatx-review.json'),fatx_before_sha256=fatx_before,fatx_after_sha256=sha(fatx),hal_before_sha256=hal_before,")
        s=s.replace('Only rebuilt HAL and helper payloads differ; FATX0101/video0093 unchanged.','Both cases use identical candidate0102 HAL; rebuilt FATX control0101/candidate0103 and helper payloads differ. Video0093 unchanged.')
    if name=='preflight.py':
        s=s.replace("hal=read(k/'hal-review.json')[case]", "hal=read(k/'hal-review.json')['candidate001']")
        s=s.replace("sha(k/'artifacts'/hal['name'])", "sha(k.parent/'hal-dump-path/artifacts'/hal['name'])")
        s=s.replace("assert sha(k/'probe.c')", "assert sha(k/'fatx-review.json')==f['fatx_review_sha256']\nfatx=read(k/'fatx-review.json')[case]\nassert sha(k/'artifacts'/fatx['name'])==f['fatx_after_sha256']==fatx['sha256']\nassert sha(k/'probe.c')")
        start=s.index("paths+=");end=s.index('\nr=dict',start)
        s=s[:start]+"paths+=['hal-review.json','fatx-review.json','dump-map.inc','map-tests.json','0103-vfat-paging-dump-mapping.patch','inputs.json','control-inputs.json','manifest.json','prepare-source.py','test-map.c','test-map.py','setup-kit.py','build.py','build-control.py','review-fatx.py','fatx-build-candidate001.json','fatx-build-control001.json','atomic_json.py']"+s[end:]
    if name=='audit.py':
        s=s.replace('root dump-accounting HAL; both serial mode, FATX0101/video0093 unchanged', 'FATX dump mapping; both serial mode, identical candidate0102 HAL/video0093')
    p.write_text(s)
(k/'hal-review.json').write_bytes((old/'hal-review.json').read_bytes())
print('Created paired runtime scripts; no guest prepared/launched')
