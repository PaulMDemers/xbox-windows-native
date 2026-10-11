"""Existing complete captures only; retain differences from239/241 controls."""
import ast,hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'directory-delta001.json';assert not dest.exists()
original=k.parent/'gpu-reference-snapshot238/directory-delta.py';tree=ast.parse(original.read_text(encoding='utf-8'));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inventory');exec(compile(ast.Module(body=[fn],type_ignores=[]),str(original),'exec'))
before,base=inventory(k.parent/'gpu-preserve-entry239/seed001/before/artifacts/directories.bin');rows=[];sets={}
for kit,case in [('gpu-preserve-entry239','control001'),('gpu-preserve-empty241','preserve001'),('gpu-reference-pair242','preserve001'),('gpu-reference-pair243','preserve001')]:
 out=k.parent/kit/case;files,row=inventory(out/'artifacts/directories.bin');a=json.loads((out/'allocation.json').read_text(encoding='utf-8'));assert row['files']==a['files'] and row['directories']==a['directories']
 label=out.relative_to(ws).as_posix();sets[label]=files;row.update(case=label,added=sorted(files-before),absent=sorted(before-files));assert not row['absent'];rows.append(row)
candidate=sets['outputs/gpu-reference-pair243/preserve001'];control=sets['outputs/gpu-preserve-entry239/control001'];prior=sets['outputs/gpu-preserve-empty241/preserve001']
r=dict(passed=True,parser_source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),before=base,cases=rows,candidate_only_vs_control=sorted(candidate-control),control_only_vs_candidate=sorted(control-candidate),candidate_only_vs241=sorted(candidate-prior),prior241_only=sorted(prior-candidate),scope='Path inventory from existing closed captures only; not file-byte/power-loss qualification',recollection=False,physical_access=False)
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({key:r[key] for key in ['candidate_only_vs_control','control_only_vs_candidate','candidate_only_vs241','prior241_only']}))
