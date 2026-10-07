"""Check whether the eventual target bytes already existed in immutable backing slack."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002'];out=k/case
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
dest=out/'before-target.json';assert not dest.exists()
f=read(k/('fixture-'+case+'.json'));base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert sha(base.read_bytes())==f['fixture_sha256']
run=ws/('work/runs/nt5-fatx-paging-buffer-'+case);assert (run/'cleanup.json').exists()
al=read(out/'alignment.json');layout=read(out/'layout-comparison.json')['emulator_after']
at=layout['absolute_byte_offset'];n=al['expected_warning_bytes'];cold=(out/'artifacts/after-setupapi.log').read_bytes();expected=cold[al['desired_offset']:al['desired_offset']+n]
assert sha(cold)==al['after_sha256'] and len(expected)==n
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
with ColdIO(base) as io:io.seek(at);before=io.read(n)
with ColdIO(run/'hdd.qcow2') as io:io.seek(at);after=io.read(n)
assert after==expected
(out/'artifacts/before-target-raw.bin').write_bytes(before)
r=dict(scope=__doc__,case=case,physical_access=False,fixture_sha256=f['fixture_sha256'],absolute_byte_offset=at,target_cluster=layout['target_cluster'],
       before_sha256=sha(before),after_sha256=sha(after),before_first111_sha256=sha(before[:111]),after_first111_sha256=sha(after[:111]),
       first111_already_match=before[:111]==after[:111],following109_already_match=before[111:]==after[111:],full_target_already_matches=before==after,
       differing_byte_count=sum(a!=b for a,b in zip(before,after)),before_all_zero=not any(before),
       limits='Compares the eventual physical byte range in the immutable input and closed output. It does not assume the input FAT chain owned this range; no active disk read or first physical-console topology claim.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
