"""Stage reviewed0101 and the unchanged prior004 helper in an actual pre-GPU-install fixture."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
case=sys.argv[1];assert case=='001'
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'shutdown-install-idle/fixture-002.json').read_text())
prior=k.parent/'shutdown-installer-completion'
review=json.loads((k/'helper-review.json').read_text());helper=(prior/'artifacts/probe.exe').read_bytes()
assert m.sha((k/'probe.c').read_bytes())==review['source_sha256']
assert json.loads((k.parent/'fatx-append-sequence/002/qualification.json').read_text())['passed']
assert review['passed'] and m.sha(helper)==review['probe_sha256']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name']
parent_hash=r['fixture_sha256'];assert m.filehash(parent)==parent_hash
target=parent.with_name(('fatx-first-install-0101-'+case+'.qcow2'));seed=ws/('work/fatx-first-install-0101-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
preserved={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/xwn-video-trace.bin']}
inv=json.loads((k.parent/'fatx-append-sequence/first-install-inventory.json').read_text())['fixtures']['pre_install']
assert preserved['winnt/system32/config/system']==inv['hashes']['system']
assert preserved['winnt/system32/config/software']==inv['hashes']['software']
assert not inv['gpu'].get('Driver') and inv['gpu']['ConfigFlags']==1024
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
m.replace(w,'xwnidle/probe.exe',helper)
driver=Path('/home/paul/xbox-windows-native/build/fatx-directory-order-001/build-fatx/drivers/filesystems/vfatfs/vfatfs.sys').read_bytes()
assert m.sha(driver)==json.loads((k.parent/'fatx-directory-order/binary-review.json').read_text())['sha256']=='ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9'
r['prior_fatx_sha256']=m.sha(w.read('winnt/system32/drivers/xwnfatx.sys'))
assert r['prior_fatx_sha256']==r['fatx_sha256']=='beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd'
m.replace(w,'winnt/system32/drivers/xwnfatx.sys',driver);r['fatx_sha256']=m.sha(driver);w.flush()
for row in r['payloads']:
    if row['path']=='xwnidle/probe.exe':row.update(sha256=m.sha(helper),bytes=len(helper))
    if row['path']=='winnt/system32/drivers/xwnfatx.sys':row.update(sha256=m.sha(driver),bytes=len(driver))
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
assert m.sha(fresh.read('winnt/system32/drivers/xwnfatx.sys'))==r['fatx_sha256']
for p in ['xwnidle/result.log','xwnidle/windows.log']:
    try:fresh.read(p)
    except KeyError:pass
    else:raise AssertionError('Pre-install output already exists: '+p)
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,
         fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         preserved_during_observer_staging=preserved,source_manifest='shutdown-install-idle/fixture-002.json',
         probe_review_manifest='shutdown-installer-completion/004/probe-review.json',probe_source_manifest='shutdown-installer-completion/004/probe.c',
         intervention='Replace FATX0098 with reviewed0101 and use exact previously tested setup-completion helper; no hive/startup edits; window samples, pending-install status, one verified GPU Finish and one same-process exact restart-prompt No; block restart if queue remains pending. Cancel only exact command-line-identified 1B36:0005 placeholder welcome page. No other unknown dialog action.',
         limits='Guest observer changes timing; no host recorder/debugger; no stability or hardware qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print('Observer fixture prepared')
