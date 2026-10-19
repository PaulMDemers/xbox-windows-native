"""Map retained retail bytes to the supplied disc for a smaller future helper ISO."""
import hashlib,io,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pycdlib
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
media=next(r for r in json.loads((K.parent/'rct559/media001.json').read_text()) if r['sha256']=='7910b1440239f7026821507180e6dfdbc5a119147baaf77c4e542182c1ad9052')
p=Path(media['path']);assert sha(p)==media['sha256'] and p.stat().st_size==media['bytes']
package=K.parent/'rct565/package001.json'
files={n:r for n,r in json.loads(package.read_text())['files'].items() if n.startswith('game/')}
for row in files.values():assert sha(Path(row['path']))==row['sha256']
sizes={r['bytes'] for r in files.values()};available={}
iso=pycdlib.PyCdlib();iso.open(str(p))
try:
 for row in media['files']:
  if row['bytes'] not in sizes:continue
  out=io.BytesIO();iso.get_file_from_iso_fp(out,joliet_path=row['path']);b=out.getvalue();assert len(b)==row['bytes']
  available.setdefault(hashlib.sha256(b).hexdigest(),[]).append(row['path'])
finally:iso.close()
mapped={};supplement={}
for name,row in files.items():
 if row['sha256'] in available:mapped[name]=dict(source=sorted(available[row['sha256']])[0],bytes=row['bytes'],sha256=row['sha256'])
 else:supplement[name]=dict(bytes=row['bytes'],sha256=row['sha256'],private_path=row['path'])
r=dict(completed=True,read_only=True,source_iso=dict(path=str(p),bytes=media['bytes'],sha256=media['sha256']),package_sha256=sha(package),mapped_files=mapped,supplemental_files=supplement,mapped_bytes=sum(r['bytes'] for r in mapped.values()),supplemental_bytes=sum(r['bytes'] for r in supplement.values()),physical_access=False,runtime_launched=False,source_sha256=sha(Path(__file__)),limits='Read-only byte identity mapping. No new ISO/fixture allocated, no copy script or two-CD guest behavior validated. A future helper must verify source-disc identity and reconstruct all destinations before launch.')
out=K/'disc-mapping001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(mapped_files=len(mapped),mapped_bytes=r['mapped_bytes'],supplemental_files=len(supplement),supplemental_bytes=r['supplemental_bytes'])))
