"""MIT. Independently validate private BMP format and compare selected pixels.

Run with bundled Pillow Python. Pixel deltas are not a semantic game verdict.
"""
import hashlib,json,re,struct
from pathlib import Path
from PIL import Image,ImageChops
K=Path(__file__).resolve().parent;P=Path('C:/xwn574/pc001/collection001')
out=K/'capture-review001.json';assert not out.exists()
col=json.loads((K/'collection001.json').read_text());assert col['completed']
rows={};images={}
manifest=json.loads(Path('C:/xwn574/pc001/cold1-002/manifest.json').read_text())
runner=(P/'runner.txt').read_text()
sources={tag:(name,int(size)) for tag,name,size in re.findall(r'^game_screenshot=(\S+) source=(.+?) bytes=(\d+) copied=1 tick=\d+$',runner,re.M)}
for path in sorted(list(P.glob('*.bmp'))+list(P.glob('*.shot'))):
    data=path.read_bytes();h=hashlib.sha256(data).hexdigest()
    expected=col['files']['xwn574/'+path.name]
    assert h==expected['sha256'] and len(data)==expected['bytes']
    tag=path.stem[3:]
    if path.suffix=='.bmp':
        magic,size,res1,res2,offset=struct.unpack_from('<2sIHHI',data)
        dib,w,ht,planes,bpp,compression,imagebytes=struct.unpack_from('<IiiHHII',data,14)
        assert (magic,size,res1,res2,offset,dib,w,ht,planes,bpp,compression,imagebytes)==(b'BM',len(data),0,0,54,40,640,-480,1,32,0,640*480*4)
        assert len(data)==54+640*480*4
        method='GDI'
    else:
        name,size=sources[tag];assert len(data)==size and 0<size<=4*1024**2
        original=manifest['xwn574-kit/game/'+name.lower()]
        assert original['sha256']==h and original['bytes']==size
        method='game Screenshot'
    decoded=Image.open(path);fmt=decoded.format
    assert fmt in ['BMP','PCX','PNG']
    im=decoded.convert('RGB');assert im.size==(640,480)
    images[tag]=im
    rows[tag]=dict(path=str(path),sha256=h,bytes=len(data),unique_rgb=len(set(im.get_flattened_data())),format=fmt,method=method)
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
r=dict(structurally_valid=bool(rows),all_images_nonuniform=bool(rows) and all(r['unique_rgb']>1 for r in rows.values()),complete_case_matrix=all(mode+'-'+step in images for mode in ['window','full'] for step in ['before','edge','arrow','drag']),captures=rows,comparisons=pairs,physical_access=False,limits='Private GDI and game-produced images. Inspect landscape independently and compare passive QMP display evidence. A game-produced screenshot is not display/scanout proof. No FPS or acceleration measurement.')
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(captures=len(rows),comparisons=pairs)))
