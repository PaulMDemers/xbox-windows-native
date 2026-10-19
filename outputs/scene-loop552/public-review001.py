import json,hashlib
from pathlib import Path
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/scene-loop552')
p=Path('/home/paul/xbox-windows-native/scene-loop552-public001');b=json.loads((p/'build.json').read_text());q=json.loads((k/'sample-build001.json').read_text())
assert b['exit_code']==0 and b['source_sha256']==q['source_sha256'] and b['compiler_sha256']==q['compiler_sha256']
assert hashlib.sha256((p/'sceneloop.exe').read_bytes()).hexdigest()==b['executable_sha256']
(k/'public-build001.json').write_text(json.dumps(dict(compiled=True,source_matches=True,compiler_matches=True,public_executable_sha256=b['executable_sha256'],runtime_executable_sha256=q['executable_sha256'],same_binary=b['executable_sha256']==q['executable_sha256'],public_binary_runtime_qualified=False,receipt_path=str(p/'build.json'),receipt_sha256=hashlib.sha256((p/'build.json').read_bytes()).hexdigest()),indent=2)+'\n')
print('Public build/source match; rebuilt binary runtime not claimed')
