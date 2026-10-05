"""Losslessly compress one closed owned CPU trace, verifying bytes before removing the original."""
import argparse,gzip,hashlib,json,pathlib,shutil
ws=pathlib.Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run.startswith('nt5-') and a.run.replace('-','').isalnum()
run=(ws/'work/runs'/a.run).resolve();assert run.parent==(ws/'work/runs').resolve()
assert (run/'cleanup.json').exists()
source=run/'cpu-trace.log';target=run/'cpu-trace.log.gz';assert source.is_file() and not target.exists()
stat=source.stat()
with source.open('rb') as f:expected=hashlib.file_digest(f,'sha256').hexdigest()
with target.open('xb') as output:
    with gzip.GzipFile(filename='',mode='wb',fileobj=output,compresslevel=6,mtime=0) as compressed:
        with source.open('rb') as f:shutil.copyfileobj(f,compressed,1024*1024)
with gzip.open(target,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
assert source.stat().st_size==stat.st_size and source.stat().st_mtime_ns==stat.st_mtime_ns
with source.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
r=dict(scope=__doc__,run=a.run,original_bytes=stat.st_size,compressed_bytes=target.stat().st_size,uncompressed_sha256=expected,roundtrip_verified=True)
(run/'trace-compression.json').write_text(json.dumps(r,indent=2)+'\n')
source.unlink();print(json.dumps(r,indent=2))
