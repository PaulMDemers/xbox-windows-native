"""Retain bounded primary-source inputs privately; publish identities and findings."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn734/references001');P.mkdir()
out=K/'references001.json';assert not out.exists()
refs=[('linux-nv_hw.c','https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/video/fbdev/nvidia/nv_hw.c'),('linux-nvreg.h','https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/gpu/drm/nouveau/dispnv04/nvreg.h'),('linux-crtc.c','https://raw.githubusercontent.com/torvalds/linux/v6.12/drivers/gpu/drm/nouveau/dispnv04/crtc.c'),('envy-nv_vga.xml','https://raw.githubusercontent.com/envytools/envytools/f102b82381f3f11cee113d16374c87091db039d9/rnndb/display/nv_vga.xml')]
r={'completed':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':{}}
try:
 for name,url in refs:
  with urllib.request.urlopen(url,timeout=20) as f:body=f.read(300001)
  assert len(body)<=300000
  (P/name).write_bytes(body)
  r['files'][name]={'url':url,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
 r['completed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('Primary-source inputs retained privately; metadata only published')
