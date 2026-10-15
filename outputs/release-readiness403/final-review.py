"""Read completed evidence and original pins; never run/build/collect a guest."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda name:json.loads((K/name).read_text(encoding='utf-8'))
frozen=load('emu001/emulator-frozen.json')
assert all(sha(W/p)==h for p,h in frozen.items())
docs=load('docs-invariants002.json');assert all(docs[n]['all_exact'] for n in ['399','401'])
correction=load('emu001/corrected-analysis003.json');a=correction['analysis']
assert sha(K/'emu001/audit.json')==correction['original_audit_sha256']
assert a['scoped_combined_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1
assert not a['strict_qualification_passed'] and not a['physical_qualified']
assert all(n['rejected'] for n in correction['negative_controls'])
assert load('emu001/closure.json')['closed']
closed=json.loads(Path('C:/xwn403/runs/nt5-restore403-emu001/host-exit.json').read_text())
assert closed['closed'] and closed['exit_code']==0 and not closed['fallback_kill']
restore=load('install-restore003.json');assert restore['restore']['status']=='verified'
assert restore['restored_readback_files']==6571 and restore['restore']['outside_before']==restore['restore']['outside_after']
assert restore['restore']['e_after']==restore['backup']['e_sha256']
assert load('hal-correspondence003.json')['all_differences_in_timestamp_or_checksum']
assert load('network-correspondence001.json')['all_differences_in_timestamp_or_checksum']
assert not load('input-provenance003.json')['unresolved']
build=load('build-verification002.json');assert len(build['profiles'])==8 and build['artifact_count_with_settings']==11
export=load('export-verification001.json');assert len(export['profiles'])==8 and all(p['reference_match'] for p in export['profiles'])
package=load('source-package002.json');assert sha(Path(package['archive']))==package['sha256']
names=['hal-correspondence003.json','network-correspondence001.json','input-provenance003.json','build-verification002.json','dependency-fetch002.json','install-restore003.json','factory-roots001.json','emu001/audit.json','emu001/corrected-analysis003.json','emu001/closure.json','emu001/allocation.json','source-package002.json','export-verification001.json','unit-tests001.json','docs-invariants002.json','correspondence-controls001.json']
r={'completed_scoped_work':True,'public_release_ready':False,'frozen_emulator_inputs_exact':len(frozen),'older_release_inputs_exact':71,'profiles_built':8,'artifacts_with_settings':11,'toolchain_receipt_files':6587,'prepared_restore_files':6571,'restored_emulator_scoped_pass':True,'strict_emulator_pass':False,'strict_failure':'Ftdisk49 retained','physical_access':False,'owned_emulator_closed':closed,'source_review_package':package,'remaining':['Fresh owned-media assembly and registry provisioning','Pristine supported-host prerequisite validation','Physical installation/recovery qualification','Final component licensing and curated export review'],'records_sha256':{n:sha(K/n) for n in names}}
with (K/'final-review.json').open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
print(json.dumps({n:v for n,v in r.items() if n not in ['records_sha256','source_review_package']}))
