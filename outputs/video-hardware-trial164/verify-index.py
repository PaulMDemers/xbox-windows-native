"""Check the staged evidence bytes against existing immutable runtime pins."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

k = Path(__file__).resolve().parent
ws = k.parents[1]
folders = ['video-physical-review159', 'video-physical-rehearsal160',
           'video-physical-rehearsal161', 'video-physical-rehearsal162',
           'video-physical-diagnostic163', 'video-hardware-trial164',
           'video-helper-runtime165']
sha = lambda b: hashlib.sha256(b).hexdigest()
tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ws).decode().split('\0'))
changed = set(subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ws).decode().split('\0'))
inherited_newlines = {}
pins = disk = index = syntax = 0
for folder in folders:
    root = k.parent / folder
    for p in root.rglob('*.py'):
        ast.parse(p.read_text(encoding='utf-8'))
        syntax += 1
    for p in root.rglob('*frozen-inputs.json'):
        manifest = json.loads(p.read_text(encoding='utf-8'))
        assert isinstance(manifest, dict)
        pins += 1
        for name, digest in manifest.items():
            assert isinstance(digest, str) and len(digest) == 64, str(p)
            assert sha((ws / name).read_bytes()) == digest, name
            disk += 1
            if name in tracked:
                data = subprocess.check_output(['git', 'show', ':' + name], cwd=ws)
                if sha(data) != digest:
                    # Previously committed text may have Git LF normalization while
                    # runtime pins deliberately describe the executed Windows bytes.
                    assert name not in changed, 'Index changed frozen bytes: ' + name
                    raw = (ws / name).read_bytes()
                    assert raw.replace(b'\r\n', b'\n') == data.replace(b'\r\n', b'\n'), name
                    inherited_newlines[name] = dict(runtime_sha256=digest,
                        existing_index_sha256=sha(data), newline_only=True,
                        staged_change=False)
                index += 1
review = json.loads((k / 'controller-source-review.json').read_text(encoding='utf-8'))
ready = json.loads((k / 'hardware-diagnostic-ready.json').read_text(encoding='utf-8'))
assert review['controller_sha256'] == ready['controller_sha256'] == sha((k / 'physical-controller.py').read_bytes())
result = dict(passed=True, manifests=pins, disk_pins=disk, indexed_pins=index,
              parsed_python_sources=syntax, physical_deployment_performed=False,
              frozen_runtime_sources_changed=False,
              inherited_git_newline_normalization=inherited_newlines)
(k / 'index-verification.json').write_bytes((json.dumps(result, indent=2) + '\n').encode('utf-8'))
print(json.dumps(result))
