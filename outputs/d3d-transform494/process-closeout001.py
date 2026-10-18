"""Read-only process inventory, avoiding shell regex/pipe argument translation."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'process-closeout001.json';assert not out.exists()
rows=[]
for p in Path('/proc').glob('[0-9]*/cmdline'):
 try:
  args=p.read_bytes().split(b'\0');name=args[0].rsplit(b'/',1)[-1].decode('ascii',errors='replace')
  if name in ('qemu-system-i386','qemu-system-x86_64','qemu-nbd','nbdfuse'):rows.append(dict(pid=int(p.parent.name),name=name))
 except OSError:pass
assert not rows,rows
out.write_text(json.dumps(dict(passed=True,read_only=True,running_QEMU_NBD_FUSE=rows),indent=2)+'\n');print('No QEMU/NBD/FUSE processes.')
