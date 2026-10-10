"""Bounded primary-source reference capture; these are leads, not NV2A grants."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'references.json';assert not dest.exists()
out=k/'artifacts/references';out.mkdir(parents=True,exist_ok=False);rows=[]
urls={
 'linux-v6.12-nv04-instmem.c':'https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/gpu/drm/nouveau/nvkm/subdev/instmem/nv04.c',
 'envytools-nv10-pfb.xml':'https://raw.githubusercontent.com/envytools/envytools/master/rnndb/memory/nv10_pfb.xml'}
for name,url in urls.items():
 with urllib.request.urlopen(url,timeout=20) as response:
  data=response.read(262145);assert len(data)<=262144
  rows.append(dict(name=name,url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),etag=response.headers.get('ETag')))
 (out/name).write_bytes(data)
assert b'base.reserved = 512 * 1024;' in (out/'linux-v6.12-nv04-instmem.c').read_bytes()
assert b'PRAMIN_WR_PROT' in (out/'envytools-nv10-pfb.xml').read_bytes()
dest.write_text(json.dumps(dict(passed=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),references=rows,
 guest_launch=False,physical_access=False,gpu_register_access=False,
 limits='Linux NV04-family allocation and envytools reverse-engineering register descriptions are primary implementation/reference leads. Neither identifies the actual NV2A physical PRAMIN mapping in this retained Xbox boot path. master capture is content-hash pinned, not a claimed immutable upstream revision.'),indent=2)+'\n',encoding='utf-8')
