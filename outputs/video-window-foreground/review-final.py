"""Review final measurement evidence and frozen guest inputs; no guest operation."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dest=k/'final-review.json';assert not dest.exists()
pair=read(k/'pair-review.json');model=read(k/'redraw-model.json');pe=read(k/'pe-review.json')
assert pair['passed'] and model['passed'] and pe['passed']
assert pair['script_sha256']==sha(k/'compare.py') and model['source_sha256']==sha(k/'redraw-model.py')
assert pe['probe_sha256']==sha(k/'artifacts/probe.exe') and pe['probe_source_sha256']==sha(k/'probe.c')
assert pe['display_sha256']=='ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8'
assert pe['control_display_sha256']=='a1d5cf1eea27729a23c06e177f89f862eedcff0a1d0aa002815f4456279b4e98'
runs=[]
for case in ['control001','candidate001']:
 out=k/case;v=read(out/'verification.json');audit=read(out/'audit.json');f=read(k/('fixture-'+case+'.json'));closure=read(out/'closure.json')
 assert v['passed'] and v['ordinary_qualified'] and not v['physical_qualified'] and v['profile_attribution_passed']
 assert len(v['cases'])==18 and len(v['references'])==18 and len(v['observed_readbacks'])==36 and v['compared_pixels']==3538944
 assert len(audit['hives'])==5 and all(row['parsed'] for row in audit['hives']) and not audit['warnings_errors']
 for name,digest in v['pins'].items():assert sha(out/name)==digest
 for name,digest in read(out/'preflight.json')['sources'].items():assert sha(out/'source'/name)==digest
 assert sha(out/'source/probe.c')==sha(k/'probe.c') and sha(out/'source/protocol.py')==sha(k/'protocol.py')
 assert pair['pins'][case]==model['pins'][case]==sha(out/'verification.json')
 run=ws/('work/runs/nt5-vforeground-'+case);assert (run/'cleanup.json').exists()
 assert sha(run/'cleanup.json')==closure['run_metadata_sha256']['cleanup.json']
 runs.append(dict(case=case,strict_passed=True,closed=True,verification_sha256=sha(out/'verification.json'),fixture_sha256=f['fixture_sha256']))
for kit in ['video-window-move','video-window-observe']:
 old=k.parent/kit;assert not read(old/'control001/verification.json')['passed'] and read(old/'control001/audit.json')['integrity_passed']
 assert (old/'control001/closure.json').exists()
assert not (ws/'work/runs/nt5-vmove-candidate001').exists() and (k.parent/'video-window-move/fixture-candidate001.json').exists()
oldanalysis=read(k.parent/'video-window-observe/control001/pixel-analysis.json')
assert len(oldanalysis['rows'])==36 and all(r['bounds']==[270,100,384,256] for r in oldanalysis['rows'])
assert not pair['timing_qualified']
r=dict(passed=True,runs=runs,probe_sha256=pe['probe_sha256'],display_sha256=pe['display_sha256'],failed_attempts_preserved=True,old_candidate_prepared_never_launched=True,driver_changes=False,physical_access=False,timing_qualified=False,model_sha256=sha(k/'redraw-model.json'),pair_sha256=sha(k/'pair-review.json'),reviewer_sha256=sha(Path(__file__)))
dest.write_text(json.dumps(r,indent=2)+'\n');print('Final movement measurement review passed; all owned attempts closed')
