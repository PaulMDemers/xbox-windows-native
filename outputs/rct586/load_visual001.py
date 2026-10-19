"""MIT. Independent private framebuffer comparison; no image editing or game writes."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageChops
K=Path(__file__).resolve().parent;P=Path('C:/xwn586/pc001')
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
paths={
 'saved':P/'collection001/06-park-after-save.bmp',
 'new_game':P/'phase2/screen-1792441988959321081.png',
 'camera_changed':P/'phase2/screen-1792442005922649382.png',
 'load_dialog':P/'phase2/screen-1792442037078929125.png',
 'load_path':P/'phase2/screen-1792442052568365015.png',
 'loaded':P/'phase2/screen-1792442067821857785.png',
}
ims={n:Image.open(p).convert('RGB') for n,p in paths.items()}
for n in ['new_game','camera_changed','loaded']:
 assert ims[n].size==(1024,768);ims[n]=ims[n].crop((36,55,676,535))
assert ims['saved'].size==(640,480)
# Interior scenery, excluding top/bottom UI and the pointer's before/after locations.
box=(10,60,470,420)
def comparison(a,b):
 aa=ims[a].crop(box);bb=ims[b].crop(box)
 count=sum(x!=y for x,y in zip(aa.getdata(),bb.getdata()))
 return dict(changed_pixels=count,total_pixels=aa.width*aa.height,
  exact=count==0,first_sha256=hashlib.sha256(aa.tobytes()).hexdigest(),second_sha256=hashlib.sha256(bb.tobytes()).hexdigest())
r=dict(platform='Owned PC QEMU; no Xbox qualification',
 observed='Load Game dialog listed XWN586.SV4 after normal restart. Exact saved path selected. Park entrance and path returned after deliberate right-arrow camera movement.',
 roi=box,camera_changed=comparison('new_game','camera_changed'),
 loaded_vs_saved=comparison('saved','loaded'),
 files={n:dict(path=str(p),sha256=sha(p)) for n,p in paths.items()},
 limitation='One windowed paused-scene control; not all serialized game state, game performance, audio or physical FATX persistence.')
r['passed']=r['camera_changed']['changed_pixels']>50000 and r['loaded_vs_saved']['exact']
out=K/'load-visual001.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','camera_changed','loaded_vs_saved']}))
