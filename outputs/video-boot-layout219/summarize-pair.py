"""Preserve exact oversized pair result and index a compact lossless-reference summary."""
import hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;path=k/'pair-review.json';archive=k/'artifacts/pair-review-full.json';assert not archive.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=sha(path);original=json.loads(path.read_text());assert original['passed'] and path.stat().st_size>=5*1024*1024
shutil.copyfile(path,archive);assert sha(archive)==before
summary=dict(original)
summary['cases']={}
for name,case in original['cases'].items():
 compact={a:b for a,b in case.items() if a!='sequence_samples'}
 compact['sequence_samples']=[dict(passed=v['passed'],all_159_snapshot_transitions_monotonic=v['all_159_snapshot_transitions_monotonic']) for v in case['sequence_samples']]
 assert len(compact['sequence_samples'])==5 and all(v['passed'] for v in compact['sequence_samples']);summary['cases'][name]=compact
summary['original_full_review']=dict(private_path=archive.relative_to(k).as_posix(),sha256=before,bytes=archive.stat().st_size,preserved_exact=True)
summary['summary_author_sha256']=sha(Path(__file__))
summary['summary_limits']='Only redundant decoded sequence packet tables omitted from compact index. Exact full result retained privately; tracked closed audits and pinned raw inputs retain actual evidence. Review source/frozen inputs/gates unchanged; no guest rerun.'
blob=(json.dumps(summary,indent=2)+'\n').encode();assert len(blob)<5*1024*1024
path.write_bytes(blob);assert sha(archive)==before
(k/'repository-size-failure001.json').write_text(json.dumps(dict(check='tools/check-repository.py',failure='pair-review.json >=5MiB',kind='Host packaging only; no source/guest/test failure',original_full_sha256=before,original_preserved=str(archive.relative_to(k)),resolved_by='compact pair index with private full exact result and existing tracked closed audits',qualification_gates_changed=False,guest_relaunched=False),indent=2)+'\n')
print('Exact full pair preserved; compact index bytes:',len(blob))
