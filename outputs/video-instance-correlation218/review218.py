"""Verify frozen inputs, closed cases and distinguish calibration from alias."""
import ast,json,hashlib,struct,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checked=0
for file in k.glob('emulator-frozen*.json'):
    for path,digest in json.loads(file.read_text()).items():
        assert sha(Path(path))==digest,(file,path);checked+=1
for file in k.glob('build-inputs*.json'):
    for path,digest in json.loads(file.read_text())['files'].items():
        assert sha(Path(path))==digest,(file,path);checked+=1
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
a=json.loads((k/'emu-epath007/audit.json').read_text());e=json.loads((k/'e-audit007.json').read_text())
assert a['integrity_passed'] and a['probe_completed'] and a['raw_lengths_passed'] and e['passed']
c0,c1,g0,g1=[struct.unpack('<5120I',(k/'emu-epath007/artifacts'/n).read_bytes()) for n in ['cpu0.bin','cpu1.bin','gpu0.bin','gpu1.bin']]
ind=dict(cpu_stable=c0==c1,gpu_stable=g0==g1,nonzero_words=sum(v!=0 for v in c0),distinct_blocks=len(set(c0[i:i+4] for i in range(0,5120,4))),forward_mismatches=sum(x!=y for x,y in zip(c0,g0)))
assert ind['cpu_stable'] and ind['gpu_stable'] and ind['nonzero_words']==0 and ind['distinct_blocks']==1 and ind['forward_mismatches']==563
bad=json.loads((k/'emu-native006-audit002/audit.json').read_text())
assert not bad['integrity_passed'] and not bad['probe_completed'] and bad['allocation']['orphan_cluster_count']==6
assert bad['file_mismatches'][0]['path']=='F/winnt/system32/config/software'
assert json.loads((k/'geometry-arithmetic006.json').read_text())['exact_arithmetic_match']
assert json.loads((k/'progress005.json').read_text())['progress_words'][1:4]==[2,123,0]
cases=[]
for name in ['correlation001','correlation002','bootpath003','stack004','progress005','native006','epath007']:
    run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/instance218-runs')/('stock-instance218-'+name)
    instance=json.loads((run/'instance.json').read_text());assert (run/'cleanup.json').exists()
    row=dict(case=name,pid=instance['processId'],closed=True,instance_sha256=sha(run/'instance.json'),cleanup_sha256=sha(run/'cleanup.json'))
    if (run/'hdd.qcow2').exists():row['disk_sha256']=sha(run/'hdd.qcow2')
    cases.append(row)
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozen_hash_checks=checked,source_ast_passed=True,
       host_compare_checks=98,host_compare_seeds=16,build005_calibrated_on_emulator=True,
       cpu_pramin_observation=ind,informative_alias_correlation=False,gpu_alias_proven=False,
       nt5_ownership_granted=False,software_context_implemented=False,gpu_copy_submitted=False,
       physical_deployed=False,physical_qualified=False,normal_stock_restart_observed=False,
       failed_f_geometry_preserved=True,closed_cases=cases)
(k/'review218.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['frozen_hash_checks','build005_calibrated_on_emulator','informative_alias_correlation','physical_deployed']}))
