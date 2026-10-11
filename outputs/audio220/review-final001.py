"""Final independent local evidence/source review; no console or shared build access."""
import ast,hashlib,json,pathlib,subprocess
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
dest=k/'final-review001.json';assert not dest.exists()
assert subprocess.check_output(['git','branch','--show-current'],cwd=repo).decode().strip()=='codex/xbox-native-audio'
parsed=[]
for p in sorted(k.glob('*.py')):ast.parse(p.read_text(encoding='utf-8-sig'));parsed.append(p.name)
frozen={}
for manifest in ['frozen001.json','frozen002.json']:
    rows=read(k/manifest);frozen[manifest]=len(rows)
    for path,h in rows.items():assert sha(pathlib.Path(path))==h,(manifest,path)
cases={}
for case,audit,gate in [('install001','audit002.json','scoped_installation_passed'),('playback001','audit.json','scoped_runtime_passed')]:
    out=k/case;a=read(out/audit);closure=read(out/'closure.json')
    assert closure['closed'] and closure['audit_sha256']==sha(out/audit)
    assert a[gate] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return']
    assert a['strict_qualification_passed'] is False and a['audibility_observed'] is False
    assert [(v['source'],v['event_id']) for v in a['warnings_errors']]==[('Ftdisk',49)]
    cases[case]=dict(audit=audit,sha256=sha(out/audit),scoped_passed=True,strict_passed=False,audibility_observed=False)
restored=read(k/'restored001/restoration.json');confirmation=read(k/'restored001/confirmation.json');allocation=read(k/'restored001/allocation.json')
assert restored['completed'] and restored['baseline_restored'] and all(restored['checks'].values())
assert confirmation['passed'] and confirmation['dashboard_owner_verified'] and all(v['matched'] for v in confirmation['checks'].values())
assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
for n in ['install001','playback001','restored001']:
    assert read(k/n/'scan.json')['snapshot_complete'] and read(k/n/'scan-return.json')['dashboard_return']
r=dict(passed=True,scope=__doc__,python_sources_parsed=parsed,frozen_manifests=frozen,cases=cases,restoration_sha256=sha(k/'restored001/restoration.json'),confirmation_sha256=sha(k/'restored001/confirmation.json'),restored_readback_files=len(restored['checks']),final_allocation=dict(directories=allocation.get('directories'),files=allocation.get('files'),orphan_cluster_count=allocation['orphan_cluster_count'],errors=allocation['errors']),physical_audio_qualified=False,audibility_unobserved=True,source_package_commit='7cdb191bd2ef72e24001370726f97a7383a7250b')
dest.write_text(json.dumps(r,indent=2)+'\n')
logs={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(k.glob('*.log')) if not p.name.startswith(('final-review','push'))}
(k/'host-log-pins001.json').write_text(json.dumps(logs,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','frozen_manifests','restored_readback_files','physical_audio_qualified','audibility_unobserved']},indent=2))
