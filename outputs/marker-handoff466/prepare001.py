"""Flatten only the pinned never-executed seed to a new C-owned fixture."""
import hashlib,json,shutil,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('/mnt/c/xwn466/preparation001');S=Path('/mnt/e/xwn412/preparation002/fresh.qcow2')
out=K/'preparation001.json';assert not out.exists() and not O.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((K.parent/'handoff-trace412/preparation002.json').read_text())
assert p['never_executed_seed'] and sha(S)==p['fixture_sha256']
assert shutil.disk_usage('/mnt/c').free-2*1024**3>=20*1024**3
chain=json.loads(subprocess.check_output(['qemu-img','info','--backing-chain','--output=json',str(S)]))
pins={str(Path(v['filename']).resolve()):sha(Path(v['filename'])) for v in chain}
O.mkdir(parents=True);r=dict(status='preparing',physical_access=False,seed_never_executed=True,parent_chain=pins)
try:
 subprocess.run(['qemu-img','convert','-f','qcow2','-O','qcow2',str(S),str(O/'seed.qcow2')],check=True,timeout=180)
 c=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(S),str(O/'seed.qcow2')],capture_output=True,text=True,timeout=180)
 assert c.returncode==0,c.stdout+c.stderr
 info=json.loads(subprocess.check_output(['qemu-img','info','--output=json',str(O/'seed.qcow2')]))
 assert 'backing-filename' not in info and info['virtual-size']==10000000000
 check=json.loads(subprocess.check_output(['qemu-img','check','--output=json',str(O/'seed.qcow2')]))
 assert not check.get('corruptions',0) and not check.get('leaks',0)
 for path,h in pins.items():assert sha(Path(path))==h
 r.update(status='prepared',complete_virtual_equality=True,comparison=c.stdout,info=info,qcow_check=check,
          seed_sha256=sha(O/'seed.qcow2'),seed=str(O/'seed.qcow2'),source_chain_unchanged=True)
except BaseException as e:r.update(status='failed',error=repr(e));raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
