"""MIT. Read-only plan for host NTFS compression, retaining historical inputs."""
import ctypes, json
from pathlib import Path
K=Path(__file__).resolve().parent
W=K.parents[1]
out=K/'archive-plan005.json'
assert not out.exists()
pins={}
for manifest in (W/'work/runs').glob('*/input-hashes.json'):
    for row in json.loads(manifest.read_text(encoding='utf-8-sig')):
        if 'Path' not in row or 'Hash' not in row: continue
        p=Path(row['Path'])
        if p.parent!=W/'work' or not p.name.startswith('physical-') or p.suffix!='.qcow2': continue
        pins.setdefault(p,[]).append((row['Hash'].lower(),str(manifest)))
f=ctypes.WinDLL('kernel32',use_last_error=True).GetCompressedFileSizeW
f.argtypes=[ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_ulong)]
f.restype=ctypes.c_ulong
rows=[]
for p,entries in pins.items():
    if not p.is_file() or len({h for h,_ in entries})!=1: continue
    s=p.stat()
    hi=ctypes.c_ulong(); lo=f(str(p),ctypes.byref(hi)); allocated=(hi.value<<32)+lo
    if s.st_size<900_000_000 or allocated<s.st_size: continue
    rows.append(dict(path=str(p),bytes=s.st_size,allocated_bytes=allocated,sha256=entries[0][0],manifest=entries[0][1]))
rows=sorted(rows,key=lambda r:r['path'])[:30]
assert rows
out.write_text(json.dumps(dict(scope='Existing pinned physical input archives; host compression only',files=rows),indent=2)+'\n')
print('Planned',len(rows),'archives')
