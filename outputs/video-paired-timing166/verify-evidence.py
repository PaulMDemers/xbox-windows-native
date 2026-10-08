"""Verify frozen source, staged bytes and completed stage records without reruns."""
import ast,hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'evidence-verification.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
checked=0
for name,digest in read(k/'frozen-inputs.json').items():
    assert sha((ws/name).read_bytes())==digest,name
    if name.startswith('outputs/video-paired-timing166/') and '/artifacts/' not in name:
        assert sha(subprocess.check_output(['git','show',':'+name],cwd=ws))==digest,name
    checked+=1
for name,digest in read(k/'physical-ready.json')['source_pins'].items():
    assert sha((k/name).read_bytes())==digest,name
    path=str((k/name).relative_to(ws)).replace('\\','/')
    assert sha(subprocess.check_output(['git','show',':'+path],cwd=ws))==digest,path
for case in ['control001','candidate001']:
    assert read(k/case/'closure.json')['closed']
    r=read(k/case/'physical.json')
    assert r['launch_requested'] and r.get('collected_utc') and r['baseline_restored'] and not r['startup_enabled']
    assert read(k/case/'physical-return.json')['closed'] and read(k/case/'restored-verification.json')['passed']
for p in k.rglob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
for label in ['upload','copy-alias']:
    row=next(v for v in read(k/'upload-instructions.json')['results'] if v['label']==label)
    assert sha((k/(label+'-disassembly.txt')).read_bytes())==row['stdout_sha256']
assert read(k/'paired-physical.json')['scoped_paired_timing_passed']
result=dict(passed=True,source_pins_checked=checked,physical_sources_exact=True,
    raw_instruction_output_exact=True,owned_runs_closed=True,physical_launches=2,
    physical_collections=2,source_or_guest_reruns=0,strict_release_qualified=False)
dest.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'))
print(json.dumps(result))
