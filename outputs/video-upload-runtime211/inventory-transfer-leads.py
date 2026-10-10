"""Read-only pinned local NV2A source leads; no MMIO or transfer qualification."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'transfer-source-leads.json';assert not dest.exists()
base=Path('/home/paul/ogxbox-linux/build/fresh-20260930/xemu-nvnet')
revision=(base/'.source-revision').read_text().strip();assert revision=='e72e76bd1f12ce45c6c63b4196c6918ea2cc705d'
pattern=re.compile(r'IMAGE_BLIT|IMAGE_FROM_CPU|MEMORY_TO_MEMORY|NV09F|NV062')
files=[base/'hw/xbox/nv2a/nv2a_regs.h',*sorted((base/'hw/xbox/nv2a/pgraph').rglob('*.c')),*sorted((base/'hw/xbox/nv2a/pgraph').rglob('*.h'))]
rows={}
for p in files:
 if not p.exists():continue
 data=p.read_bytes();matches=[dict(line=i,text=line.strip()) for i,line in enumerate(data.decode().splitlines(),1) if pattern.search(line)]
 if matches:rows[p.relative_to(base).as_posix()]=dict(sha256=hashlib.sha256(data).hexdigest(),matches=matches)
assert rows
r=dict(passed=True,source_revision=revision,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),files=rows,
 guest_launch=False,physical_access=False,transfer_qualified=False,
 limits='Pinned local emulator source names/method leads only; not hardware documentation, NT5 integration or register programming evidence. CPU fallback, pinned DMA memory, exclusive channel/context ownership, ordering/completion, clipping/overlap and crash residency remain required before any isolated prototype.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({name:len(row['matches']) for name,row in rows.items()},indent=2))
