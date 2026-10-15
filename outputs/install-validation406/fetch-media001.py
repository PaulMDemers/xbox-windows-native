"""Private CES footage download, exact catalog hash and bounded byte count."""
import hashlib,json,shutil,time,urllib.parse,urllib.request
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('E:/xwn406/media001');P.mkdir(parents=True,exist_ok=False)
item='youtube-WMZa-tNwAzQ';meta_url='https://archive.org/metadata/'+item
meta=json.load(urllib.request.urlopen(meta_url,timeout=30))
row=next(f for f in meta['files'] if f['name'].endswith('.mp4'))
size=int(row['size']);assert size==19845173
assert shutil.disk_usage(P).free-size-8*1024**2>=20*1024**3
url='https://archive.org/download/'+item+'/'+urllib.parse.quote(row['name'])
dest=P/'ces2001-source.mp4';deadline=time.monotonic()+300
with urllib.request.urlopen(url,timeout=30) as r,dest.open('xb') as f:
    assert urllib.parse.urlparse(r.url).hostname.endswith('.archive.org') or urllib.parse.urlparse(r.url).hostname=='archive.org'
    count=0
    while b:=r.read(1024*1024):
        count+=len(b);assert count<=size and time.monotonic()<deadline;f.write(b)
assert count==size
with dest.open('rb') as f:assert hashlib.file_digest(f,'sha1').hexdigest()==row['sha1']
with dest.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
(P/'archive-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
record=dict(item=item,title=meta['metadata']['title'],archive_url='https://archive.org/details/'+item,
            download_url=url,original_url=meta['metadata']['originalurl'],catalog_sha1=row['sha1'],sha256=digest,
            bytes=count,private_path=str(dest),rights='Third-party footage retained privately for requested playback test; no redistribution license asserted and excluded from public source/package.',
            playback_verified=False,source='Giant Bomb archived CES 2001 segment; historical event corroborated by Microsoft January 6, 2001 announcement')
with (K/'media-source001.json').open('x') as f:json.dump(record,f,indent=2);f.write('\n')
print(json.dumps(record))
