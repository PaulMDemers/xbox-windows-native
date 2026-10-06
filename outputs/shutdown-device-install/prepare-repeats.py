"""Make two independent seeds of the exact pre-run002 installed state."""
import importlib,json,shutil,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sys.path.insert(0,str(k.parent/'native-windows-paint-save'));m=importlib.import_module('prepare-fixture')
sys.path.insert(0,str(k.parent/'fatx-mapped-eof'));from coldio import ColdIO
r=json.loads((k/'fixture-002.json').read_text())
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/r['fixture_name']
seed=ws/'work/shutdown-device-install-002-seed.qcow2'
assert m.filehash(base)==r['fixture_sha256'] and m.filehash(seed)==r['seed_sha256']
info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(seed)]))
# Seed relative backing path is interpreted after the owned runner copies it.
assert info['backing-filename']=='../../../outputs/native-windows-fatx-forensics/artifacts/'+base.name
m.fatx.PARTITIONS['F']=(15633072*512,472764096*512)
with ColdIO(base) as io:
 w=m.Writer(io,m.fatx.open_partition(io,base,'F'))
 for name in ['result.log','matched.log']:
  try:w.read('xwns99/'+name)
  except KeyError:pass
  else:raise AssertionError('Repeat source already contains workload result')
 for row in r['payloads']:assert m.sha(w.read(row['path']))==row['sha256']
 for path,sha in r['preserved_during_staging'].items():assert m.sha(w.read(path))==sha
for case in ['003','004']:
 target=ws/('work/shutdown-device-install-'+case+'-seed.qcow2');manifest=k/('fixture-'+case+'.json')
 assert not target.exists() and not manifest.exists()
 shutil.copyfile(seed,target);assert m.filehash(target)==r['seed_sha256']
 out=dict(r,repeat_of='002',repeat_case=case,independent_repeat=True,
  repeat_scope='Exact immutable pre-run002 disk; independent writable runtime overlay. Not a consecutive reboot.',
  fresh_workload_logs_verified_absent=True)
 manifest.write_text(json.dumps(out,indent=2)+'\n')
print('Two independent seeds verified; no guest or physical launch')
