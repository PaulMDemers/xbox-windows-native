"""Change only the FATX executable in a child of the retained installed-package fixture."""
import importlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(ws/'outputs/native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
case=sys.argv[1] if len(sys.argv)>1 else '001';assert case in ['001','002']
parent='005' if case=='001' else '004'
base=ws/('outputs/native-windows-fatx-forensics/artifacts/video-nt5-display-package-'+parent+'.qcow2')
r=json.loads((k.parent/('video-nt5-display-package/fixture-'+parent+'.json')).read_text());expected=r['fixture_sha256'];assert m.filehash(base)==expected
build=json.loads((k/'build-report.json').read_text());assert build['status']=='compiled'
target=base.with_name('fatx-paging-eof-'+case+'.qcow2');seed=ws/('work/fatx-paging-eof-'+case+'-seed.qcow2')
assert not target.exists() and not seed.exists()
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(base),str(target)],check=True)
m.target=target;m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
io=m.SliceIO(target);w=m.Writer(io,m.fatx.open_partition(io,target,'F'))
path='winnt/system32/drivers/xwnfatx.sys';old=w.read(path);assert m.sha(old)=='0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336'
driver=(k/'artifacts/xwnfatx.sys').read_bytes();assert m.sha(driver)==build['artifacts'][0]['sha256']
unchanged={p:m.sha(w.read(p)) for p in ['winnt/system32/config/system','winnt/system32/config/software','winnt/system32/config/default']}
m.replace(w,path,driver);w.flush()
fresh=m.Writer(io,m.fatx.open_partition(io,target,'F'));assert fresh.read(path)==driver
for p,h in unchanged.items():assert m.sha(fresh.read(p))==h
for row in r['payloads']:assert m.sha(fresh.read(row['path']))==row['sha256']
r['payloads'].append(dict(path=path,sha256=m.sha(driver),bytes=len(driver)))
assert m.filehash(base)==expected
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b',base.name,str(target)],check=True)
subprocess.run(['qemu-img','create','-f','qcow2','-F','qcow2','-b',str(target),str(seed)],check=True)
subprocess.run(['qemu-img','rebase','-u','-f','qcow2','-F','qcow2','-b','../../../outputs/native-windows-fatx-forensics/artifacts/'+target.name,str(seed)],check=True)
r.update(scope=__doc__,parent_fixture_sha256=expected,fixture_sha256=m.filehash(target),seed_sha256=m.filehash(seed),
         fatx_before_sha256=m.sha(old),fatx_sha256=m.sha(driver),hives_unchanged=unchanged,
         system_unchanged_during_staging=True,registry_hives_unchanged_during_staging=True,
         expected_start=1 if case=='001' else 3,
         installation_method='Existing installed package state retained; only FATX executable replaced. See expected_start.')
(k/('fixture-'+case+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('One-payload FATX candidate fixture verified '+case)
