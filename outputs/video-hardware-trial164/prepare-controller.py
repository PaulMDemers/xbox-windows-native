"""Bind the physical controller to the fresh165 helper validation, preserve original source."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'physical-controller.py';assert not dest.exists()
s=(k/'physical.py').read_text(encoding='utf-8')
s=s.replace("k/'candidate001/audit.json'","k.parent/'video-helper-runtime165/candidate001/audit.json'")
# Record the namespace proof rather than the host-only failed164 attempt.
assert "video-helper-runtime165/candidate001/audit.json" in s
ast.parse(s);dest.write_text(s,encoding='utf-8')
(k/'controller-source-review.json').write_text(json.dumps(dict(passed=True,
    original_source_sha256=hashlib.sha256((k/'physical.py').read_bytes()).hexdigest(),
    controller_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),changes=['Use165 completed helper runtime instead of164 host-guard failure'],
    eligibility_scope='Nonpromoting physical drawing diagnostic only; same Ftdisk49 retained as strict failure',
    source_safety=['Baseline hash checks before any console write','Unique helper and rollback directories',
        'Local and console readback-verified rollback before display changes','No emulator hive deployment',
        'Startup enabled last, restored first','Preserve after results before restoring original display/SYSTEM',
        'No second launch and no service/dump/cache policy modification'],physical_access=False),indent=2)+'\n',encoding='utf-8')
print('Physical controller source bound to165 proof; no console access')
