"""Freeze a configured child of the reviewed406 owned runtime, not old attempts."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;old=K.parent/'install-validation406'
assert not (K/'Invoke001.ps1').exists()
changed={}
for name in ['Invoke001.ps1','start-owned.ps1','close-host.py']:
 source=(old/name).read_text();s=source
 if name=='Invoke001.ps1':s=s.replace('E:/xwn406/runs','E:/xwn424/runs').replace('/mnt/e/xwn406/runs','/mnt/e/xwn424/runs').replace('E:/xwn406/assembly003/fresh.qcow2','E:/xwn424/assembly001/fresh.qcow2').replace('../../assembly003/fresh.qcow2','../../assembly001/fresh.qcow2')
 (K/name).write_text(s,newline='\n');changed[name]={'parent_sha256':hashlib.sha256((old/name).read_bytes()).hexdigest(),'child_sha256':hashlib.sha256((K/name).read_bytes()).hexdigest(),'configuration_only':True}
s=(old/'supervise001.py').read_text().replace('nt5-validation406-','nt5-crypto424-').replace('E:/xwn406/runs','E:/xwn424/runs')
(K/'supervise001.py').write_text(s,newline='\n')
s=(old/'logon-owned001.py').read_text();(K/'logon-owned001.py').write_text(s,newline='\n')
s=(old/'type-witness001.py').read_text().replace('XWN409','XWN423BIN').replace('probe.exe','create.exe');(K/'type-witness001.py').write_text(s,newline='\n')
(K/'host-lineage001.json').write_text(json.dumps(changed,indent=2)+'\n')
