"""MIT. Independently validate private BMP format and compare selected pixels.

Run with bundled Pillow Python. Pixel deltas are not a semantic game verdict.
"""
import hashlib,json,struct
from pathlib import Path
from PIL import Image,ImageChops
K=Path(__file__).resolve().parent;P=Path('C:/xwn573/pc001/collection001')
out=K/'capture-review001.json';assert not out.exists()
col=json.loads((K/'collection001.json').read_text());assert col['completed']
rows={};images={}
for path in sorted(P.glob('*.bmp')):
    data=path.read_bytes();h=hashlib.sha256(data).hexdigest()
    expected=col['files']['xwn573/'+path.name]
    assert h==expected['sha256'] and len(data)==expected['bytes']
    magic,size,res1,res2,offset=struct.unpack_from('<2sIHHI',data)
    dib,w,ht,planes,bpp,compression,imagebytes=struct.unpack_from('<IiiHHII',data,14)
    assert (magic,size,res1,res2,offset,dib,w,ht,planes,bpp,compression,imagebytes)==(b'BM',len(data),0,0,54,40,640,-480,1,32,0,640*480*4)
    assert len(data)==54+640*480*4
    im=Image.open(path).convert('RGB');assert im.size==(640,480)
    tag=path.stem[3:];images[tag]=im
    rows[tag]=dict(path=str(path),sha256=h,bytes=len(data),unique_rgb=len(set(im.get_flattened_data())))
pairs={}
for mode in ['window','full']:
    previous=mode+'-before'
    for action in ['edge','arrow','drag']:
        current=mode+'-'+action
        if previous in images and current in images:
            a=images[previous].crop((5,40,635,430));b=images[current].crop((5,40,635,430))
            changed=sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data()))
            pairs[mode+'-'+action]=dict(before=previous,after=current,roi=[5,40,635,430],pixels=630*390,changed=changed,bbox=ImageChops.difference(a,b).getbbox())
        previous=current
r=dict(structurally_valid=bool(rows),complete_case_matrix=all(mode+'-'+step in images for mode in ['window','full'] for step in ['before','edge','arrow','drag']),captures=rows,comparisons=pairs,physical_access=False,limits='Private native GDI captures. Pixel changes are not sufficient evidence of landscape movement; inspect UI state and landscape independently. No FPS or acceleration measurement.')
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(captures=len(rows),comparisons=pairs)))
