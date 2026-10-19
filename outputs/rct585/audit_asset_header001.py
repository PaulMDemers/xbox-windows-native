"""Independently compare generated C integrity metadata with verified assets."""
import ast,hashlib,json,re
from pathlib import Path
K=Path(__file__).resolve().parent
expected=json.loads((K/'asset-integrity001.json').read_text())
rows=re.findall(r'\{("(?:[^"\\]|\\.)*"),(\d+),\{([\d,]+)\}\}',(K/'assets.h').read_text())
assert len(rows)==502
differences=[]
for literal,size,digest in rows:
    name=ast.literal_eval(literal).replace('\\','/')
    actual=dict(bytes=int(size),sha1=bytes(map(int,digest.split(','))).hex())
    want={k:expected[name][k] for k in actual}
    if actual!=want:differences.append(dict(name=name,generated=actual,expected=want))
r=dict(passed=not differences,rows=len(rows),differences=differences,source_sha256=hashlib.sha256((K/'assets.h').read_bytes()).hexdigest(),cause='Unrestricted attempt-number replacement modified numeric asset metadata. Guest verifier stopped before game launch.',physical_access=False)
out=K/'asset-header-review001.json';assert not out.exists()
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
