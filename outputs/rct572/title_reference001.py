"""MIT. Select hash-only title patches stable across retained real positive frames."""
import hashlib,json
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent;out=K/'title-reference001.json';header=K/'title_signature.h'
assert not out.exists() and not header.exists()
paths=[Path('C:/xwn568/pc001/phase1/screen-1792393853300892324.png'),Path('C:/xwn571/pc001/phase1/auto-1792398269315148364.png'),Path('C:/xwn571/pc001/phase1/screen-1792398282862878619.png'),Path('C:/xwn571/pc001/collection001/00-title-not-ready.bmp')]
negative=Path('C:/xwn569/pc001/collection001/00-title.bmp')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
images=[Image.open(p).convert('RGB') for p in paths]
images=[im.crop((36,55,676,535)) if im.size==(800,600) else im for im in images]
assert all(im.size==(640,480) for im in images)
bad=Image.open(negative).convert('RGB')
def fnv(im,x,y):
    h=2166136261;colors=set()
    for rgb in im.crop((x,y,x+16,y+16)).get_flattened_data():
        colors.add(tuple(c>>4 for c in rgb))
        for c in rgb:h=((h^(c>>4))*16777619)&0xffffffff
    return h,len(colors)
candidates=[]
for y in range(16,96,4):
    for x in range(444,620,4):
        values=[fnv(im,x,y) for im in images]
        if len({h for h,_ in values})==1 and values[0][1]>=5 and fnv(bad,x,y)[0]!=values[0][0]:
            candidates.append(dict(x=x,y=y,width=16,height=16,fnv=values[0][0],colors=values[0][1]))
assert candidates
first=next(r for r in candidates if (r['x'],r['y'])==(500,40))
others=[r for r in candidates if abs(r['x']-first['x'])>=20 or abs(r['y']-first['y'])>=20]
assert others
second=sorted(others,key=lambda r:(-r['colors'],r['y'],r['x']))[0]
rows=[first,second]
assert all(len({fnv(im,r['x'],r['y'])[0] for im in images})==1 for r in rows)
header.write_bytes(('/* MIT. Hash-only stable title reference; see title-reference001.json. */\nstatic const DWORD title_signatures[2][3]={\n'+''.join(' {%d,%d,0x%08xUL},\n'%(r['x'],r['y'],r['fnv']) for r in rows)+'};\n').encode())
out.write_text(json.dumps(dict(passed=True,positive_frames=[dict(path=str(p),sha256=sha(p),native_gdi=p.suffix=='.bmp') for p in paths],negative=dict(path=str(negative),sha256=sha(negative)),rectangles=rows,candidate_count=len(candidates),old_second_hashes=[fnv(im,540,70)[0] for im in images],all_selected_positive_frames_match=True,negative_rejected=True,physical_access=False,limits='Readiness image controls only. These frames establish stability for the sampled title scenes, not every future frame or native input behavior.'),indent=2)+'\n')
print(json.dumps(rows))
