"""Read-only examination of preserved physical damaged bytes and owned recovery files."""
import hashlib,json,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
source=ws/'outputs/physical-gpu-setup/log-anomaly.json';raw=source.read_bytes();original=json.loads(raw)
b=bytes.fromhex(original['malformed_range_hex']);assert len(b)==111
out=k/'analysis.json';assert not out.exists()
root=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files');assert root.is_dir()
needles={'full111':b,'first24':b[:24],'middle24':b[42:66],'last24':b[-24:]}
r=dict(scope=__doc__,physical_access=False,source=str(source),source_sha256=hashlib.sha256(raw).hexdigest(),length=len(b),minimum=min(b),maximum=max(b),high_bit_count=sum(v>=128 for v in b),del_count=b.count(127),mean_absolute_difference_by_lag={str(n):sum(abs(a-c) for a,c in zip(b,b[n:]))/(len(b)-n) for n in range(1,13)},residue_channels=[dict(residue=n,values=list(b[n::3]),minimum=min(b[n::3]),maximum=max(b[n::3])) for n in range(3)],search_root=str(root),searched_files=0,searched_bytes=0,matches=[],read_errors=[],needle_sha256={n:hashlib.sha256(v).hexdigest() for n,v in needles.items()})
started=time.monotonic()
for path in sorted(root.rglob('*')):
    if not path.is_file():continue
    r['searched_files']+=1;at=0;tail=b'';seen=set()
    try:
        with path.open('rb') as f:
            while True:
                chunk=f.read(1024*1024)
                if not chunk:break
                data=tail+chunk;r['searched_bytes']+=len(chunk)
                for name,needle in needles.items():
                    cursor=0
                    while True:
                        where=data.find(needle,cursor)
                        if where<0:break
                        offset=at-len(tail)+where;cursor=where+1
                        if (name,offset) not in seen:
                            seen.add((name,offset));r['matches'].append(dict(path=str(path.relative_to(root)),needle=name,offset=offset))
                at+=len(chunk);tail=data[-110:]
    except OSError as exc:r['read_errors'].append(dict(path=str(path.relative_to(root)),error=repr(exc)))
r['elapsed_seconds']=time.monotonic()-started
r['interpretation']='Strong three-byte periodicity is a source-identification lead, not proof of pixels, stale disk data, a video-driver overwrite, or a reset cause. Search covers only saved recovery files, not original pre-write slack, RAM, compressed/decoded image surfaces, or the physical disk.'
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['length','high_bit_count','mean_absolute_difference_by_lag','searched_files','searched_bytes','matches','read_errors','elapsed_seconds']},indent=2))
