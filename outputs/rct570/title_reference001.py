"""MIT. Hash-only UI readiness reference from retained private screenshots."""
import hashlib,json
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent;out=K/'title-reference001.json';header=K/'title_signature.h'
assert not out.exists() and not header.exists()
pos=Path('C:/xwn568/pc001/phase1/screen-1792393853300892324.png')
neg=Path('C:/xwn569/pc001/collection001/00-title.bmp')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=Image.open(pos).convert('RGB').crop((36,55,676,535));b=Image.open(neg).convert('RGB')
def fnv(image,rect):
    value=2166136261;colors=set()
    for rgb in image.crop(rect).get_flattened_data():
        colors.add(tuple(c>>4 for c in rgb))
        for c in rgb:value=((value^(c>>4))*16777619)&0xffffffff
    return value,len(colors)
rows=[]
for x,y in [(500,40),(540,70)]:
    rect=(x,y,x+16,y+16);expected,colors=fnv(a,rect);negative,_=fnv(b,rect)
    assert expected!=negative and colors>=3
    rows.append(dict(x=x,y=y,width=16,height=16,fnv=expected,negative_fnv=negative,quantized_colors=colors))
header.write_text('/* MIT. Hash-only quantized title-logo reference. */\nstatic const DWORD title_signatures[2][3]={\n'+''.join(' {%d,%d,0x%08xUL},\n'%(r['x'],r['y'],r['fnv']) for r in rows)+'};\n')
out.write_text(json.dumps(dict(positive=dict(path=str(pos),sha256=sha(pos),client=[36,55,640,480]),negative=dict(path=str(neg),sha256=sha(neg)),algorithm='FNV1a32 over row-major RGB high nibbles, two16x16 logo rectangles',rectangles=rows,negative_rejected=True,physical_access=False,limits='Title readiness reference only; does not qualify subsequent menu or gameplay behavior.'),indent=2)+'\n')
print('Two title rectangles distinguished from the licence splash.')
