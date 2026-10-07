"""Stage coordinated draw/helper in a fresh child of the preserved aligned pre-install fixture."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];case=sys.argv[1];assert case in ['001','002']
if case=='002':assert json.loads((k/'001/qualification.json').read_text())['passed']
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
r=json.loads((k.parent/'fatx-install-alignment/fixture-001.json').read_text())
review=json.loads((k/'probe-review.json').read_text());helper=(k/'artifacts/probe.exe').read_bytes()
assert review['passed'] and m.sha(helper)==review['probe_sha256']
assert m.sha((k/'probe.c').read_bytes())==review['source_sha256'] and m.sha((k/'Build.ps1').read_bytes())==review['build_script_sha256']
parent=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name'];parent_hash=r['fixture_sha256']
assert m.filehash(parent)==parent_hash
name='fatx-install-draw-'+case;target=parent.with_name(name+'.qcow2');seed=ws/('work/'+name+'-seed.qcow2')
assert not target.exists() and not seed.exists() and not (k/('fixture-'+case+'.json')).exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(parent),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in r['payloads']+r['preserved_payloads']:assert m.sha(w.read(row['path']))==row['sha256']
protected=[p for p in r['preserved_during_alignment_staging'] if p!='xwnidle/probe.exe']+['winnt/setupapi.log']
preserved={p:m.sha(w.read(p)) for p in protected};assert preserved['winnt/setupapi.log']==r['alignment']['before_sha256']
assert preserved['winnt/system32/drivers/xwnfatx.sys']==r['fatx_sha256']
for p in ['xwnidle/result.log','xwnidle/windows.log','xwnidle/drawing.log','xwnidle/drawmode.txt']:
 try:w.read(p)
 except KeyError:pass
 else:raise AssertionError('Output or mode already exists: '+p)
m.replace(w,'xwnidle/probe.exe',helper)
for row in r['payloads']:
 if row['path']=='xwnidle/probe.exe':row.update(bytes=len(helper),sha256=m.sha(helper))
r['payloads'].append(w.write('xwnidle/drawmode.txt',b'0' if case=='001' else b'1'));w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'))
for row in r['payloads']+r['preserved_payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
assert all(m.sha(fresh.read(p))==sha for p,sha in preserved.items())
assert m.filehash(parent)==parent_hash
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',parent.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,case=case,physical_access=False,parent_fixture_sha256=parent_hash,source_manifest='fatx-install-alignment/fixture-001.json',fixture_name=target.name,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),preserved_during_drawing_staging=preserved,drawing_enabled=case=='002',probe_review_manifest='fatx-install-draw/probe-review.json',probe_source_manifest='fatx-install-draw/probe.c',intervention='Same reviewed helper in both cases, unchanged exact UI matcher/action functions. Add mode file0/1, private GDI worker, sampled log size and bounded stop/join before restart. Hives/startup/padded SetupAPI and drivers preserved.',limits='UI-assisted emulator diagnostic; first drawing may miss actual warning. Runtime coverage, actual offset and cold bytes must be verified; no physical qualification.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('Prepared coordinated drawing fixture '+case)
