"""Read-only closeout of the fresh matched diagnostic pair and immutable inputs."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=K/'final-review.json';assert not dest.exists()
pair=read(K/'pair-results.json');assert pair['scoped_matched_clock_coverage_passed']
build=read(K.parent/'hd-profile345/build001.json');assert read(K.parent/'hd-profile345/binary-review001.json')['passed']
r=dict(passed=False,physical_access=False,cases={},strict_qualification_passed=pair['strict_matched_qualification_passed'],performance_qualified=False)
for case in ['control001','candidate001']:
    out=K/case;run=Path('E:/xwn346/runs')/('nt5-phase346-'+case)
    a=read(out/'audit.json');c=read(out/'closure.json');assert c['closed'] and sha(out/'audit.json')==c['audit_sha256'] and sha(run/'cleanup.json')==c['cleanup_sha256']
    assert a['scoped_combined_passed'] and read(run/'host-exit.json')['passed']
    pins=read(out/'emulator-frozen.json')
    for n,h in pins.items():assert sha(W/n)==h,n
    f=read(out/'fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
    dll=Path('E:/xwn345/build001')/case/'xwnown.dll';assert sha(dll)==build['cases'][case]['sha256']
    paths={str(p.relative_to(out)).replace('\\','/'):sha(p) for p in (out/'artifacts').rglob('*') if p.is_file()}
    r['cases'][case]=dict(frozen_input_count=len(pins),capture_sha256=paths,host_exit_sha256=sha(run/'host-exit.json'),launch_sha256=sha(out/'launch.json'),audit_sha256=sha(out/'audit.json'),driver_sha256=sha(dll),closed=True)
for n,h in read(K/'supplemental-preflight003.json')['source_sha256'].items():assert sha(K/n)==h,n
assert pair['cases']['control001']['warnings_errors'] and pair['cases']['candidate001']['warnings_errors']
r.update(passed=True,source_sha256=sha(Path(__file__)),pair_results_sha256=sha(K/'pair-results.json'),supplemental_preflight_sha256=sha(K/'supplemental-preflight003.json'),limits='Both diagnostic scopes pass; strict warnings are preserved, and emulator timing gives no hardware performance qualification. Protected payloads and allocation audited; not a full all-file-content comparison.')
dest.write_text(json.dumps(r,indent=2)+'\n');print('Matched closeout, frozen inputs and private capture hashes verified')
