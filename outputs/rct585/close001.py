"""Close failed prelaunch preparation without treating desktop as game evidence."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn585/pc001')
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));from Registry import Registry
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'final001.json';assert not out.exists()
runtime=json.loads((K/'ntfs-phase1.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text())
assert runtime['closed'] and cold['complete'] and sha(P/'disk.qcow2')==runtime['disk_sha256']==cold['disk_sha256']
manifest=json.loads((P/'cold1-002/manifest.json').read_text());expected=json.loads((K/'asset-integrity001.json').read_text())
assets={}
for name,want in expected.items():
    got=manifest['xwn585-kit/'+name.lower()]
    assert (got['bytes'],got['sha256'])==(want['bytes'],want['sha256']),name
    assets[name]=got['sha256']
assert len(assets)==502 and not any(n.startswith('xwn585/') or n.endswith('.sv4') for n in manifest)
receipt=(P/'cold1-002/files/xwn585-kit/copy-verified.txt').read_text()
assert 'verified=0' in receipt and 'files=31' in receipt
def tree(phase):
    hive=Registry.Registry(str(P/f'cold{phase}-002/files/WINNT/system32/config/software'))
    try:k=hive.open('Fish Technology Group')
    except Registry.RegistryKeyNotFoundException:return None
    def sub(k):return dict(values=sorted((v.name(),v.value_type(),repr(v.value())) for v in k.values()),children={x.name():sub(x) for x in k.subkeys()})
    return sub(k)
checks=dict(actual_502_assets_match=True,game_not_launched=True,no_save_created=True,normal_restart=cold['normal_shutdown_delta']==1 and runtime['exit_code']==0 and not runtime.get('host_quit') and not runtime['deadline'],hives_clean=all(x['clean'] and x['header_valid'] and x['independent_raw_values_agree'] for x in cold['hives']),game_registry_unchanged=tree(0)==tree(1))
assert all(checks.values())
r=dict(closed=True,qualified=False,result='Failed verifier metadata; game never launched. Actual copied 502 files independently match pinned retail assets.',checks=checks,disk_sha256=runtime['disk_sha256'],physical_access=False,phase2_admitted=False,phase2_helper_built_not_run=True,copy_receipt=receipt,preserved_failures=['build001 signed comparison compiler error','asset-header-review001 KeyError on changed filename','guest verifier rejected incorrect size after 31 files','post-exit automatic screen capture FileNotFoundError with process exit 0'],pins={p.name:sha(p) for p in [K/'ntfs-phase1.json',K/'ntfs-cold1-002.json',K/'collection001.json',K/'asset-header-review002.json']})
out.write_text(json.dumps(r,indent=2)+'\n')
experiment=json.loads((K/'experiment001.json').read_text());experiment.update(overall_closed=True,phase2_admitted=False,close_reason=r['result']);(K/'experiment001.json').write_text(json.dumps(experiment,indent=2)+'\n')
print(json.dumps(checks))
