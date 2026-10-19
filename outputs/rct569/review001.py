"""MIT. Separate shutdown/registry evidence from observed input and rendering."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]; P=Path('C:/xwn569/pc001')
sys.path.insert(0,str(W/'work/python-packages'));from Registry import Registry
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
out=K/'review001.json'; assert not out.exists()
runtime=json.loads((K/'ntfs-phase1.json').read_text()); cold=json.loads((K/'ntfs-cold1-002.json').read_text()); collection=json.loads((K/'collection001.json').read_text())
assert runtime['closed'] and cold['complete'] and collection['completed']
assert sha(P/'disk.qcow2')==runtime['disk_sha256']==cold['disk_sha256']
def subtree(path):
    hive=Registry.Registry(str(path))
    try:key=hive.open('Fish Technology Group')
    except Registry.RegistryKeyNotFoundException:return None
    def node(k):return dict(values=sorted((v.name(),v.value_type(),repr(v.value())) for v in k.values()),children={x.name():node(x) for x in k.subkeys()})
    return node(key)
before=subtree(P/'cold0-002/files/WINNT/system32/config/software'); after=subtree(P/'cold1-002/files/WINNT/system32/config/software')
runner=P/'collection001/runner.txt'; lines=runner.read_text().splitlines() if runner.exists() else []
fields={}
for line in lines:
    if '=' in line and not line.startswith(('window ','module=')):
        key,value=line.split('=',1); fields.setdefault(key,[]).append(value)
modules=sorted({line.split(' size=',1)[0][7:] for line in lines if line.startswith('module=')})
checks=dict(registry_restored=before==after,runner_restored=fields.get('registry_restored')==['1'],normal_shutdown=cold['normal_shutdown_delta']==1,game_exit_zero=fields.get('game_exit')==['0'],no_forced_termination='forced_terminate' not in fields,normal_vm_exit=runtime['exit_code']==0 and not runtime.get('host_quit') and not runtime.get('deadline'),hives_clean=all(h['clean'] and h['header_valid'] and h['independent_raw_values_agree'] for h in cold['hives']))
r=dict(passed=all(checks.values()),checks=checks,runner_fields=fields,loaded_modules=modules,window_samples=sum(line.startswith('window ') for line in lines),new_system_events=cold.get('new_system_events'),physical_access=False,limits='Process, module, hive and shutdown checks only. Module presence is not a call trace; screenshot observations qualify only separately recorded input cases. No Xbox, frame-rate, acceleration or sound qualification.',pins={p.name:sha(p) for p in [K/'ntfs-phase1.json',K/'ntfs-cold0-002.json',K/'ntfs-cold1-002.json',K/'collection001.json']})
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(r['checks']))
