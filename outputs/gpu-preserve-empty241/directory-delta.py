"""Only existing cold captures; same parser as reviewed238, no disk collection."""
import ast,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'directory-delta001.json';assert not dest.exists()
original=k.parent/'gpu-reference-snapshot238/directory-delta.py';tree=ast.parse(original.read_text(encoding='utf-8'))
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory')
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(original),'exec'))
before,base=inventory(k.parent/'gpu-preserve-entry239/seed001/before/artifacts/directories.bin');rows=[];sets={}
for kit,case in [('gpu-preserve-entry239','control001'),('gpu-preserve-entry240','preserve001'),('gpu-preserve-empty241','preserve001')]:
 out=k.parent/kit/case;files,row=inventory(out/'artifacts/directories.bin');allocation=json.loads((out/'allocation.json').read_text(encoding='utf-8'));assert row['files']==allocation['files'] and row['directories']==allocation['directories']
 label=out.relative_to(ws).as_posix();sets[label]=files;row.update(case=label,added=sorted(files-before),absent=sorted(before-files));assert not row['absent'];rows.append(row)
a,b=sets['outputs/gpu-preserve-entry239/control001'],sets['outputs/gpu-preserve-empty241/preserve001']
r=dict(passed=True,parser_source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),before=base,cases=rows,candidate_only=sorted(b-a),control_only=sorted(a-b),scope='Path inventory only, existing complete captures; not file-byte durability or causality',recollection=False,physical_access=False)
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(candidate_only=r['candidate_only'],control_only=r['control_only'])))
