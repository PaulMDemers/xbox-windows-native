"""Rehash all closed private capsules and verify no owned fixture process remains."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'closeout001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def win(s):return Path('C:/'+s[7:]) if s.startswith('/mnt/c/') else Path(s)
files={};pids=[]
for n in (1,2,3):
 b=json.loads((K/f'build{n:03}.json').read_text())
 for p,v in b['files'].items():
  path=win(p);assert sha(path)==v['sha256'];files[str(path)]=v
 if n>1:
  r=json.loads((K/f'run{n:03}.json').read_text());assert r['closed']
  for c in r['cases']:
   assert c['closed'];pids.append(c['pid'])
   for p,v in c['files'].items():
    path=win(p);assert sha(path)==v['sha256'];files[str(path)]=v
code=r'''import json,hashlib
from pathlib import Path
k=Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/paging-handoff488')
pins={}
for n in (1,2,3):
 b=json.loads((k/f'build{n:03}.json').read_text())
 for p,h in b['inputs'].items():
  assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
  pins[p]=h
alive=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:s=p.read_bytes()
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if b'qemu-system-i386' in s.split(b'\0')[0] and b'xwn488-' in s:alive.append(int(p.parent.name))
assert not alive,alive
print(json.dumps(dict(input_pins=len(pins),owned_qemu_alive=alive,toolchain_unchanged=True)))
'''
proc=subprocess.run(['wsl','-d','Ubuntu','--','python3','-B','-c',code],capture_output=True,text=True,timeout=60)
assert proc.returncode==0,proc.stderr
result=json.loads(proc.stdout)
out.write_text(json.dumps(dict(passed=True,physical_access=False,private_files=len(files),files=files,closed_vm_pids=pids,wsl=result,source_sha256=sha(Path(__file__))),indent=2)+'\n')
