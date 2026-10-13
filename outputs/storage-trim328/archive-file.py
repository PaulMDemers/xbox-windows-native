"""Write and round-trip verify one lossless cold archive; never delete source."""
import hashlib,json,os,sys
from pathlib import Path
from compression import zstd
src=Path(sys.argv[1]);out=Path(str(src)+'.zst');receipt=Path(str(src)+'.archived328.json')
assert src.is_file() and not src.is_symlink() and not out.exists() and not receipt.exists()
assert os.path.normcase(os.path.realpath(src))==os.path.normcase(os.path.abspath(src))
before=src.stat();h=hashlib.sha256();size=0
with src.open('rb') as reader,out.open('xb') as raw:
    with zstd.ZstdFile(raw,'wb',level=3) as writer:
        while block:=reader.read(4*1024*1024):h.update(block);size+=len(block);writer.write(block)
after=src.stat();assert (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) and size==before.st_size
check=hashlib.sha256();count=0
with zstd.open(out,'rb') as reader:
    while block:=reader.read(4*1024*1024):check.update(block);count+=len(block)
assert count==size and check.digest()==h.digest()
compressed=hashlib.file_digest(out.open('rb'),'sha256').hexdigest()
r={'source':str(src),'archive':str(out),'original_bytes':size,'original_sha256':h.hexdigest(),
   'archive_bytes':out.stat().st_size,'archive_sha256':compressed,'roundtrip_verified':True,
   'source_removed':False,'retention':'Exact cold evidence preserved; restore to original path before historical audit or disk use'}
receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
