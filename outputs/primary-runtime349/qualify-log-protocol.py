"""Read-only correction of349 log schema; preserve original audit/closure/failure."""
import ast,copy,hashlib,json,sys
from pathlib import Path
from phase349_analysis import analyze
K=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['control001','candidate001'];out=K/case;dest=out/'log-protocol-qualification.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();a=json.loads((out/'audit.json').read_text());r=copy.deepcopy(a)
texts=[(out/f'artifacts/sample{i}/gdi-baseline.txt').read_text() for i in range(5)]
r['large_phase_samples']=[analyze(v,int(case=='candidate001')) for v in texts]
fields=['display_workload_passed','scoped_display_passed','strict_qualification_passed','scoped_combined_passed','ordinary_qualified']
# Reevaluate ONLY the exact original gate expressions, unchanged. No I/O calls,
# event exclusions or permissive substitutes. Other original audit evidence is
# retained as input; raw logs aren't recollected and original verdicts stay put.
statements=[]
for node in ast.parse((K/'audit.py').read_text()).body:
    target=node.targets[0] if isinstance(node,ast.Assign) else node.target if isinstance(node,ast.AugAssign) else None
    if isinstance(target,ast.Subscript) and isinstance(target.value,ast.Name) and target.value.id=='r' and isinstance(target.slice,ast.Constant) and target.slice.value in fields:
        statements.append(node)
assert len(statements)==8,len(statements)
source='\n'.join(ast.unparse(v) for v in statements);module=ast.Module(body=statements,type_ignores=[])
code=compile(ast.fix_missing_locations(module),'unchanged349-gates','exec');exec(code,{'r':r})
negative={}
for name in ['integrity_passed','setup_gate_passed','measurement_events_passed','orderly_host_exit','audio_probe_passed']:
    bad=copy.deepcopy(r);bad[name]=False;exec(code,{'r':bad});assert not bad['scoped_combined_passed'];negative[name]=True
q=dict(case=case,original_audit_sha256=sha(out/'audit.json'),original_raw_parser_failed=not all(v['passed'] for v in a['large_phase_samples']),original_audit_unchanged=True,correction='Actual new contiguous348 packet precedes LARGE_TIMING; validate that complete extension then use unchanged344 decoder on projection. No event/integrity/workload gate waiver.',gate_source=source,gate_source_sha256=hashlib.sha256(source.encode()).hexdigest(),audit_source_sha256=sha(K/'audit.py'),corrected_phase_samples=r['large_phase_samples'],qualified_fields={n:r[n] for n in fields},gate_negative_controls=negative,parser_sha256=sha(K/'phase349_analysis.py'),physical_access=False,performance_qualified=False)
dest.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q['qualified_fields']))
