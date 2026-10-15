"""Correct only expected profile mode using pinned303 build+actual DLL; no recollection."""
import ast,copy,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'emu001';dest=out/'corrected-analysis002.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((W/'outputs/hd-surface303/build003.json').read_text());cfg=source['cases']['candidate001'];assert source['status']==cfg['status']=='compiled' and cfg['definitions']['XWN_BODY_PROFILE']=='OFF'
r=json.loads((out/'audit.json').read_text());original=copy.deepcopy(r)
row=next(x for x in r['files'] if x['path'].lower()=='e/winnt/system32/xwnown.dll');assert row['matched'] and row['before_sha256']==row['after_sha256']==cfg['sha256']=='b23b94ac12c9f507e3d905d9de905dcff9a8fd53c2fba4336fb830e97666101d'
pins=json.loads((out/'emulator-frozen.json').read_text());assert all(sha(W/p)==h for p,h in pins.items())
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from timing_analysis import timing;from window_analysis import window
sys.path.insert(0,str(W/'outputs/hd-phase344'));from phase_analysis import analyze as large_phase
texts=[(out/'artifacts'/('sample%d/gdi-baseline.txt'%i)).read_text() for i in range(5)]
for key,fn in [('phase_samples',timing),('window_samples',window),('large_phase_samples',large_phase)]:
 r[key]=[fn(v,0) for v in texts];assert all(v['passed'] for v in r[key]),key
negative=[]
for i,log in enumerate(texts):
 for name,fn,needle in [('timing',timing,'PROFILE_BEFORE_kind_index_value 0 3 0'),('window',window,'WINDOW_PROFILE_index_value 0 3 0'),('large',large_phase,'PHASE344_BEFORE 0 3 0')]:
  assert needle in log
  for mutation,bad in [('wrong-mode',log.replace(needle,needle[:-1]+'1',1)),('missing-packet-field',log.replace(needle+'\n','',1))]:
   assert not fn(bad,0)['passed'];negative.append({'sample':i,'parser':name,'mutation':mutation,'rejected':True})
# Evaluate the original aggregate expressions unchanged, in original source order.
module=ast.parse((K/'audit.py').read_text())
keys={'display_workload_passed','scoped_display_passed','scoped_combined_passed','strict_qualification_passed','ordinary_qualified'}
selected=[]
for node in module.body:
 target=node.targets[0] if isinstance(node,ast.Assign) and len(node.targets)==1 else node.target if isinstance(node,ast.AugAssign) else None
 if isinstance(target,ast.Subscript) and isinstance(target.value,ast.Name) and target.value.id=='r' and isinstance(target.slice,ast.Constant) and target.slice.value in keys:
  selected.append(node)
assert len(selected)==10,len(selected)
exec(compile(ast.Module(body=selected,type_ignores=[]),'<unchanged aggregate expressions>','exec'),{'r':r})
result={'scope':'Separate corrected analysis; original audit/closure/fixture remain immutable','expected_mode':0,'mode_source_build_sha256':sha(W/'outputs/hd-surface303/build003.json'),'actual_driver_sha256':cfg['sha256'],'original_audit_sha256':sha(out/'audit.json'),'original_scoped_combined_passed':original['scoped_combined_passed'],'original_declared_fixture_mode':json.loads((out/'fixture.json').read_text())['profile_mode'],'negative_controls':negative,'aggregate_expression_count':len(selected),'analysis':r,'physical_access':False,'new_run_or_collection':False}
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['display_workload_passed','scoped_combined_passed','strict_qualification_passed','normal_shutdown_count','integrity_passed']}))
assert r['scoped_combined_passed'] and not r['strict_qualification_passed']
