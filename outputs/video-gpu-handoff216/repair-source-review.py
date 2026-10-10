"""Preserve Windows newline normalization failure; restore exact shared bytes."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'source-review001-failure.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();names=['common.py','boundary_analysis.py','upload_analysis.py','runner_analysis.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py','interval_policy.py','typed-state.py']
out=k/'artifacts/initial-adapters';out.mkdir(exist_ok=False);rows=[]
for n in names:
 p=k/n;old=k.parent/'video-gpu-state214'/n;q=out/n;q.write_bytes(p.read_bytes())
 assert p.read_text(encoding='utf-8')==old.read_text(encoding='utf-8'),n
 rows.append(dict(name=n,initial_sha256=sha(p),exact_parent_sha256=sha(old),semantic_text_equal=True))
 p.write_bytes(old.read_bytes());assert sha(p)==sha(old)
p=k/'review-source.py';q=k/'review-source002.py';assert not q.exists();q.write_bytes(p.read_bytes())
dest.write_text(json.dumps(dict(preserved=True,failed_source_sha256=sha(p),failure='Bootstrap Windows write_text normalized shared LF bytes to CRLF; exact byte-equality review failed, semantic text was identical.',changes=rows,guest_launch=False,physical_access=False),indent=2)+'\n',encoding='utf-8')
