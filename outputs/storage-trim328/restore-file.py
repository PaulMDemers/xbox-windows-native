"""Restore an explicitly selected328 archive, with no overwrite or launch."""
import argparse,hashlib,json,os
from pathlib import Path
from compression import zstd
p=argparse.ArgumentParser();p.add_argument('receipt');p.add_argument('--output',help='Optional separate output path for verification; default original path')
a=p.parse_args();r=json.loads(Path(a.receipt).read_text(encoding='utf-8-sig'))
source=Path(r['source']);dest=Path(a.output) if a.output else source
archive=Path(r['archive']);assert r['roundtrip_verified']
assert archive.is_file() and not dest.exists() and dest.parent.is_dir()
with archive.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['archive_sha256']
temporary=Path(str(dest)+'.restoring328');assert not temporary.exists()
h=hashlib.sha256();size=0
with zstd.open(archive,'rb') as reader,temporary.open('xb') as writer:
    while block:=reader.read(4*1024*1024):writer.write(block);h.update(block);size+=len(block)
    writer.flush();os.fsync(writer.fileno())
assert size==r['original_bytes'] and h.hexdigest()==r['original_sha256']
# Windows rename refuses an existing destination; no replacement of live data.
temporary.rename(dest)
print(json.dumps({'restored':str(dest),'bytes':size,'sha256':h.hexdigest(),'archive_retained':str(archive)}))
