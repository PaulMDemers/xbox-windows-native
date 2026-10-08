"""Repair an unexecuted controller's doubled CR; preserve all runtime source pins."""
import ast
import hashlib
import json
from pathlib import Path

k = Path(__file__).resolve().parent
p = k / 'physical-controller.py'
before = p.read_bytes()
assert b'\r\r\n' in before
after = before.replace(b'\r\r\n', b'\r\n')
assert before.decode('utf-8').splitlines() != []
# Universal-newline parsing already accepted the draft; executable syntax is identical.
assert ast.dump(ast.parse(before.decode('utf-8'))) == ast.dump(ast.parse(after.decode('utf-8')))
p.write_bytes(after)
sha = lambda data: hashlib.sha256(data).hexdigest()
for name in ['controller-source-review.json', 'hardware-diagnostic-ready.json']:
    q = k / name
    record = json.loads(q.read_text(encoding='utf-8'))
    assert record['controller_sha256'] == sha(before)
    record['controller_sha256'] = sha(after)
    q.write_bytes((json.dumps(record, indent=2) + '\n').encode('utf-8'))
(k / 'controller-format-repair.json').write_bytes((json.dumps(dict(
    before_sha256=sha(before), after_sha256=sha(after),
    ast_identical=True, physical_execution=False,
    cause='Windows newline translation of decoded CRLF draft doubled CR',
    frozen_runtime_sources_changed=False), indent=2) + '\n').encode('utf-8'))
print('Unexecuted controller format repaired; AST unchanged')
