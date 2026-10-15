"""Check every exported source byte against the Git index, not checkout EOLs."""
import json, subprocess, zipfile
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
names = subprocess.check_output(['git','diff','--cached','--name-only','-z'], cwd=W).decode().strip('\0').split('\0')
archive = Path(json.loads((K/'source-package003.json').read_text())['archive'])
with zipfile.ZipFile(archive) as z:
    entries = {n:z.read(n) for n in z.namelist() if n != 'SOURCE-MANIFEST.json'}
allnames = sorted(set(names) | set(entries))
raw = subprocess.check_output(['git','cat-file','--batch'], cwd=W, input=''.join(':'+n+'\n' for n in allnames).encode())
pos = 0; staged = {}
for n in allnames:
    end = raw.index(b'\n', pos); head = raw[pos:end].split(); assert head[1] == b'blob', (n,head)
    size = int(head[2]); pos = end+1; staged[n] = raw[pos:pos+size]; pos += size+1
assert pos == len(raw)
evidence = [n for n in names if n.startswith('outputs/clean-media404/')]
assert all(staged[n] == (W/n).read_bytes() for n in evidence)
diffs = [n for n,b in entries.items() if b != staged[n]]
assert not diffs, diffs
result = dict(staged_files=len(names), exact_evidence_files=len(evidence),
              source_bundle_entries_compared=len(entries), bundle_index_differences=diffs,
              historical_untracked_files_not_staged=True, passed=True)
with (K/'stage-review002.json').open('x') as f:
    json.dump(result,f,indent=2)
print(json.dumps(result))
