"""Unique one-shot helper namespace; retain original success/restart behavior."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'runner.c';assert not dest.exists()
old=ws/'outputs/video-trace-reuse-settled/runner.c';s=old.read_text(encoding='utf-8')
start=s.index('    if(Log==INVALID_HANDLE_VALUE) {');end=s.index('    record("ATTEMPT_ONCE',start)
s=s[:start]+'    if(Log==INVALID_HANDLE_VALUE)ExitProcess(2);\n'+s[end:]
s=s.replace('xwnrps01','xwnv164');assert 'xwnrps0' not in s
dest.write_text(s,encoding='utf-8');(k/'artifacts').mkdir(exist_ok=False)
(k/'runner-source-review.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
    original_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),changes=['Unique xwnv164 namespace','Remove second-cycle fallback; one run only'],
    child_success_required_before_normal_restart=True,physical_access=False),indent=2)+'\n',encoding='utf-8')
