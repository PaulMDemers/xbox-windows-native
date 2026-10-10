"""Check literal or exactly reversible Git newline reconstruction before commit."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
dest=k/'physical-commit-validation.json';assert not dest.exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
checks=[];private=[];external=[];count=0
records=list(k.glob('emulator-frozen*.json'))+list(k.glob('build-inputs*.json'))+[k/'physical-inputs.json']
pins={}
for f in records:
    row=json.loads(f.read_text());row=row.get('files',row)
    for name,digest in row.items():
        p=Path(name);assert sha(p.read_bytes())==digest,(f,name);pins[p]=digest;count+=1
for name,digest in json.loads((k/'physical-review001.json').read_text())['inputs'].items():
    pins[k/name]=digest
pins[Path(__file__)]=sha(Path(__file__).read_bytes())
for p,digest in pins.items():
    assert sha(p.read_bytes())==digest
    if not p.is_relative_to(ws):external.append(str(p));continue
    rel=p.relative_to(ws).as_posix()
    got=subprocess.run(['git','cat-file','blob',':'+rel],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
    if got.returncode:
        ignored=subprocess.run(['git','check-ignore','--quiet',rel])
        assert ignored.returncode==0,('Unstaged source',rel);private.append(rel);continue
    blob=got.stdout;literal=sha(blob)==digest
    working=p.read_bytes();normalized=blob.replace(b'\r\n',b'\n')
    crlf_lines=[i for i,line in enumerate(working.split(b'\n')[:-1]) if line.endswith(b'\r')]
    rebuilt=b'\n'.join(line+(b'\r' if i in crlf_lines else b'') for i,line in enumerate(normalized.split(b'\n')))
    reversible=not literal and normalized==working.replace(b'\r\n',b'\n') and rebuilt==working
    assert literal or reversible,('Unreconstructable frozen source',rel)
    checks.append(dict(path=rel,pinned_working_sha256=digest,staged_blob_sha256=sha(blob),
        literal=literal,reversible_line_endings=reversible,
        reconstruction='Normalize CR LF to LF in staged bytes, then append CR before LF at the recorded zero-based line indices; no other modifications.',
        working_crlf_line_indices=crlf_lines if reversible else []))
out=dict(passed=True,frozen_input_checks=count,staged_source_checks=len(checks),
    newline_reconstructions=sum(v['reversible_line_endings'] for v in checks),checks=checks,
    ignored_private_inputs=private,external_inputs=external,
    base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
    physical_access=False,guest_launch=False,limits='Index reconstruction only; preserves runtime byte hashes. No collected record or original gate changed.')
dest.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({n:out[n] for n in ['passed','frozen_input_checks','staged_source_checks','newline_reconstructions']}))
