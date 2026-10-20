"""MIT. Candidate scene comparisons and private contact sheet, not a Load verdict."""
import hashlib,json
from pathlib import Path
from PIL import Image,ImageDraw
K=Path(__file__).resolve().parent
col=json.loads((K/'collection001.json').read_text());assert col['completed'] and col['hook_removed']
prior=json.loads((K.parent/'rct594/collection001.json').read_text())
saved=prior['files']['/E/xwn593/06-park-after-save.bmp'];assert hashlib.sha256(Path(saved['path']).read_bytes()).hexdigest()==saved['sha256']
region=(160,80,620,440);reference=Image.open(saved['path']).convert('RGB').crop(region).tobytes()
rows=[];thumbs=[]
for n,row in sorted(col['files'].items()):
    if not n.startswith('/E/xwn586p2/') or not n.endswith('.bmp'):continue
    assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
    im=Image.open(row['path']).convert('RGB');assert im.size==(640,480)
    pixels=im.crop(region).tobytes();changed=sum(pixels[i:i+3]!=reference[i:i+3] for i in range(0,len(reference),3))
    rows.append(dict(name=n.rsplit('/',1)[1],path=row['path'],sha256=row['sha256'],changed_pixels_vs_saved=changed,compared_pixels=len(reference)//3))
    tile=Image.new('RGB',(320,265),'white');tile.paste(im.resize((320,240)),(0,25));ImageDraw.Draw(tile).text((4,5),rows[-1]['name'],fill='black');thumbs.append(tile)
assert thumbs
sheet=Image.new('RGB',(320*4,265*((len(thumbs)+3)//4)),(160,160,160))
for i,tile in enumerate(thumbs):sheet.paste(tile,((i%4)*320,(i//4)*265))
dest=Path('C:/xwn595/physical001/contact001.png');assert not dest.exists();sheet.save(dest)
out=K/'visual-inventory001.json';assert not out.exists()
out.write_text(json.dumps(dict(region=region,saved=saved,captures=rows,private_contact_sheet=str(dest),behavior_proved=False,scope='Numerical candidates for visual inspection; equality alone does not prove a Load occurred.'),indent=2)+'\n');print('Private contact sheet:',dest)
