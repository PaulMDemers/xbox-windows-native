"""MIT. Record inspected save-stage images and independent interior pixel comparison."""
import hashlib,json
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent
col=json.loads((K/'collection001.json').read_text());assert col['completed'] and col['hook_removed']
paths=[col['files']['/E/xwn593/'+name]['path'] for name in ['04-park-before-save.bmp','06-park-after-save.bmp']]
images=[Image.open(p).convert('RGB') for p in paths]
assert all(i.size==(640,480) for i in images)
region=(160,80,620,440);pixels=[list(i.crop(region).getdata()) for i in images]
changed=sum(a!=b for a,b in zip(*pixels));assert changed==0
r=dict(passed=True,method='Assistant visually inspected both decoded640x480 captures: paused Forest Frontiers entrance/road,0guests,10000cash,March Year1; no Save dialog/error after save. Independent pixel comparison excludes UI and pointer.',region=region,compared_pixels=len(pixels[0]),changed_pixels=changed,files={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths},limits='Save-stage scene remained intact. No Load performed; no serialization completeness/FPS/acceleration claim.')
out=K/'visual-review001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print('Save-stage visual review passed; equal interior pixels',len(pixels[0]))
