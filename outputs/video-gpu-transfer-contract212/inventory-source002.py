"""Freeze existing reconstructed source/ABI headers for transfer design only."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'source-inventory002.json';assert not out.exists()
src=Path('/home/paul/xbox-windows-native/build/video-upload-accounting210-001/source')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tree=subprocess.check_output(['git','-C',str(src),'write-tree']).decode().strip()
assert tree=='c8654947539246de3ce1e386e7007e124fcaa98f'
mini=src/'win32ss/drivers/miniport/xboxvmp'
files=[*sorted(mini.rglob('*.c')),*sorted(mini.rglob('*.h')),
 src/'sdk/include/reactos/drivers/xbox/xgpu.h',src/'drivers/base/bootvid/i386/xbox/bootvid.c',
 src/'sdk/include/ddk/video.h',src/'sdk/include/psdk/winddi.h',src/'sdk/include/xdk/mmfuncs.h',
 src/'win32ss/drivers/displays/framebuf/surface.c']
art=k/'artifacts/nt5-source002';assert all(p.is_file() for p in files), 'All source inputs must exist before any output creation'
art.mkdir(parents=True,exist_ok=False)
rows={}
for p in files:
 assert p.is_file(),str(p)
 name=p.relative_to(src).as_posix();q=art/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 assert sha(q)==sha(p)
 rows[name]=dict(sha256=sha(q),bytes=q.stat().st_size)
r=dict(passed=True,source_tree=tree,source_sha256=sha(Path(__file__)),files=rows,guest_launch=False,physical_access=False,
 limits='Compiled210 source and actual project ABI declarations pinned read-only. Tree does not replace individual file pins. No source mutation, register access, GPU initialization or new build.')
out.write_text(json.dumps(r,indent=2)+'\n');print('NT5 source files privately frozen:',len(rows))
