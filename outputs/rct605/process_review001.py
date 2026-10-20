"""Read procfs to check owned605 process closure without touching its runtime."""
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
 if exe in ['qemu-system-i386','qemu-nbd','python3'] and any(b'xwn605' in a or b'rct605/' in a for a in args):
  found.append(dict(pid=int(p.name),executable=exe))
r=dict(passed=not found,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),owned_processes=found,
 prior_probe_error='A PowerShell-to-WSL pgrep alternation lost quoting; shell treated pipes as commands. qemu-nbd rejected absent arguments, exit1. No process was stopped or disk opened. Replaced by procfs argv inspection.')
out.write_text(json.dumps(r,indent=2)+'\n');assert r['passed'],r
print('No remaining owned605 VM/build/cold processes')
