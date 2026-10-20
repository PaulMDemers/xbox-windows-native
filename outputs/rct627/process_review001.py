"""Check owned610 process closure through procfs without reopening its disk."""
import datetime,json,os
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'process-review001.json';assert not out.exists()
found=[]
for p in Path('/proc').iterdir():
 if not p.name.isdigit() or int(p.name)==os.getpid():continue
 try:args=(p/'cmdline').read_bytes().split(b'\0')
 except (FileNotFoundError,PermissionError,ProcessLookupError):continue
 if not args:continue
 exe=Path(os.fsdecode(args[0])).name
 if exe in ['qemu-system-i386','qemu-nbd','python3'] and any(b'xwn627' in a or b'rct627/' in a for a in args):
  found.append(dict(pid=int(p.name),executable=exe))
r=dict(passed=not found,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_processes=found)
out.write_text(json.dumps(r,indent=2)+'\n');assert r['passed'],r
print('No remaining owned610 VM/build/cold processes')
