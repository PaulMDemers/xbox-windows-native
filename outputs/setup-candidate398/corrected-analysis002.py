"""Correct only the inherited expected-driver literal; retain every original result.

No hardware operations or recollection. Aggregate expressions and field lists
are compiled directly from the frozen original auditor, not rewritten gates.
"""
from pathlib import Path
import ast,copy,hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];O=K/'candidate001';A=K/'artifacts/candidate001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
digest=lambda b:hashlib.sha256(b).hexdigest()
sha=lambda p:digest(p.read_bytes())
oldhash='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
expected='41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126'
pins=read(K/'frozen.json')
for p,h in pins.items():assert sha(W/p)==h,p
originals=[O/'audit.json',O/'candidate-analysis.json',O/'final-state.json',K/'final-review.json',K/'source-review.json',K/'audit.py']
original_hashes={p.relative_to(K).as_posix():sha(p) for p in originals}
pkg=read(K/'package.json');binary=read(K.parent/'fatx-enumeration390/binary-review.json')
assert pkg['candidate']['sha256']==binary['sha256']==expected and binary['passed']
collection=read(O/'collection.json');old=read(O/'audit.json');r=copy.deepcopy(old)
payload=(A/'tested-fatx.sys').read_bytes()
assert payload==Path(pkg['candidate']['source']).read_bytes()
assert digest(payload)==collection['tested_fatx_sha256']==expected and collection['tested_fatx_verified']
tree=ast.parse((K/'audit.py').read_bytes())
def key(node):
 if isinstance(node,ast.Assign) and len(node.targets)==1:
  t=node.targets[0]
  if isinstance(t,ast.Subscript) and isinstance(t.value,ast.Name) and t.value.id=='r' and isinstance(t.slice,ast.Constant):return t.slice.value
 return None
identities=[n for n in tree.body if key(n)=='tested_fatx_verified'];assert len(identities)==1
identity=copy.deepcopy(identities[0]);literals=[n for n in ast.walk(identity) if isinstance(n,ast.Constant) and n.value==oldhash]
assert len(literals)==1;literals[0].value=expected
def compiled(nodes):return compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(K/'audit.py'),'exec')
identity_code=compiled([identity])
def identity_check(c,b):
 env={'r':{},'collection':c,'art':A,'sha':lambda p:digest(b)}
 exec(identity_code,env);return env['r']['tested_fatx_verified']
assert identity_check(collection,payload)
negatives=[(dict(collection,tested_fatx_verified=False),payload),
 (dict(collection,tested_fatx_sha256=oldhash),payload),
 (collection,payload[:-1]),(collection,bytes([payload[0]^1])+payload[1:]),
 (collection,(K.parent/'fatx-physical394/artifacts/candidate001-before/E/winnt/system32/drivers/xwnfatx.sys').read_bytes())]
assert all(not identity_check(c,b) for c,b in negatives)
env={'r':r,'collection':collection,'art':A,'sha':sha}
exec(identity_code,env)
field_nodes=[n for n in tree.body if
 (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fields' for t in n.targets)) or
 (isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Name) and n.target.id=='fields')]
assert len(field_nodes)==3
aggregate_names=['scoped_combined_passed','strict_qualification_passed','diagnostic_workload_completed']
aggregate_nodes=[n for n in tree.body if key(n) in aggregate_names]
assert [key(n) for n in aggregate_nodes]==aggregate_names
exec(compiled(field_nodes+aggregate_nodes),env)
changed={k:{'original':old[k],'corrected':r[k]} for k in old if old[k]!=r[k]}
assert set(changed)=={'tested_fatx_verified','scoped_combined_passed','diagnostic_workload_completed'}
assert r['scoped_combined_passed'] and not r['strict_qualification_passed'] and not r['release_qualified']
paired=copy.deepcopy(read(O/'candidate-analysis.json'))
assert paired['candidate_file_scope_passed'] and paired['all_children_returned'] and paired['setup_before_files_passed']
paired.update(scoped_combined_passed=r['scoped_combined_passed'],strict_qualification_passed=r['strict_qualification_passed'])
assert all(sha(K/p)==h for p,h in original_hashes.items())
result=dict(scope='Separate corrected analysis002 of closed398; originals retained byte-exact',
 original_expected_identity_error=oldhash,correct_expected_identity=expected,
 candidate_payload_equals_frozen_build=True,negative_identity_cases_rejected=len(negatives),
 frozen_inputs_verified=len(pins),original_records_unchanged=original_hashes,
 copied_aggregate_expressions=[ast.unparse(n) for n in aggregate_nodes],
 copied_required_fields=env['fields'],changed_audit_fields=changed,
 corrected_audit=r,corrected_candidate_analysis=paired,
 strict_failure_retained='Ftdisk49',physical_release_qualified=False,
 no_hardware_access_or_recollection=True,
 limitation='Preflight incorrectly preserved the control identity literal. Corrected candidate identity is pinned independently by package, build review and exact preserved tested bytes. No predicate, event gate or original record was relaxed or rewritten. No live resident-image hash claim.')
p=O/'corrected-analysis002.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['corrected_audit','corrected_candidate_analysis','copied_aggregate_expressions','copied_required_fields']},indent=2))
