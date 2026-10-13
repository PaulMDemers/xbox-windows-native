"""Rehash closed evidence, private binaries and frozen inputs; never recollect."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];dest=K/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={}
for case in ['control001','candidate001']:
 out=K/case;run=Path('E:/xwn349/runs')/('nt5-primary349-'+case);a=read(out/'audit.json');q=read(out/'log-protocol-qualification.json')
 assert read(out/'closure.json')['closed'] and read(out/'closure.json')['audit_sha256']==sha(out/'audit.json')
 assert q['original_audit_sha256']==sha(out/'audit.json') and q['parser_sha256']==sha(K/'phase349_analysis.py')
 assert read(run/'host-exit.json')['passed'] and (run/'cleanup.json').exists()
 for name,h in read(out/'emulator-frozen.json').items():assert sha(W/name)==h,name
 f=read(out/'fixture.json');assert sha(Path(f['fixture_path_windows']))==f['fixture_sha256']
 captures={p.relative_to(out/'artifacts').as_posix():sha(p) for p in (out/'artifacts').rglob('*') if p.is_file()}
 for i,s in enumerate(q['corrected_phase_samples']):assert s['passed'],(case,i)
 rows[case]=dict(closed=True,audit_sha256=sha(out/'audit.json'),qualification_sha256=sha(out/'log-protocol-qualification.json'),launch_sha256=sha(out/'launch.json'),cleanup_sha256=sha(run/'cleanup.json'),captures=captures,frozen_inputs=len(read(out/'emulator-frozen.json')),original_raw_parser_failure_preserved=not all(v['passed'] for v in a['large_phase_samples']))
b=read(K.parent/'primary-copy348/build001.json')
for case in rows:assert sha(Path('E:/xwn348/build001')/case/'xwnown.dll')==b['cases'][case]['sha256']
probe=read(K.parent/'primary-copy348/probe/build001.json');assert sha(Path(probe['output_windows']))==probe['binary_sha256']
for name,h in read(K/'supplemental-protocol001.json')['pins'].items():assert sha(K/name)==h,name
hosts={}
for n in ['host001','host002']:
 h=read(K.parent/('primary-copy348/'+n+'.json'));root=Path('E:/xwn348')/n
 for name,digest in h['files'].items():assert sha(root/name)==digest,name
 hosts[n]=len(h['files'])
r=dict(passed=True,cases=rows,host_private_files_rehashed=hosts,driver_binaries_rehashed=True,probe_rehashed=True,read_only_closeout=True,physical_access=False,hardware_driver_unchanged=True,all_original_event_gates_retained=True,performance_qualified=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('Final private captures, binaries, failed/raw and corrected evidence verified')
