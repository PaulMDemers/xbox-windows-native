"""Validate physical cold-read images; pixel deltas are not gameplay verdicts."""
import hashlib,json,re,struct
from pathlib import Path
from PIL import Image,ImageChops
K=Path(__file__).resolve().parent
read=lambda n:json.loads((K/n).read_text(encoding='utf-8-sig'))
out=K/'capture-review001.json';assert not out.exists()
col=read('collection001.json');assert col['completed'] and col['hook_removed']
files=col['files']
def checked(row):
 p=Path(row['path']);b=p.read_bytes()
 assert len(b)==row['bytes'] and hashlib.sha256(b).hexdigest()==row['sha256']
 return p,b
runner_path,runner_bytes=checked(files['/E/xwn575/runner.txt'])
runner=runner_bytes.decode('ascii')
sources={tag:(name,int(size)) for tag,name,size in re.findall(r'^game_screenshot=(\S+) source=(.+?) bytes=(\d+) copied=1 tick=\d+$',runner,re.M)}
rows={};images={}
for name,row in sorted(files.items()):
 if not name.startswith('/E/xwn575/') or not name.endswith(('.bmp','.shot')):continue
 path,data=checked(row);tag=Path(name).stem[3:]
 if name.endswith('.bmp'):
  magic,size,res1,res2,offset=struct.unpack_from('<2sIHHI',data)
  dib,w,ht,planes,bpp,compression,imagebytes=struct.unpack_from('<IiiHHII',data,14)
  assert (magic,size,res1,res2,offset,dib,w,ht,planes,bpp,compression,imagebytes)==(b'BM',len(data),0,0,54,40,640,-480,1,32,0,640*480*4)
  assert len(data)==54+640*480*4
  method='GDI client capture'
 else:
  original_name,size=sources[tag]
  matches=[v for n,v in files.items() if n.lower()==('/E/xwn575-kit/game/'+original_name).lower()]
  assert len(matches)==1 and matches[0]['sha256']==row['sha256'] and matches[0]['bytes']==size==len(data)
  checked(matches[0]);method='game Screenshot'
 decoded=Image.open(path);fmt=decoded.format;assert fmt in ('BMP','PCX','PNG')
 im=decoded.convert('RGB');assert im.size==(640,480);images[tag]=im
 rows[tag]=dict(path=str(path),sha256=row['sha256'],bytes=len(data),unique_rgb=len(set(im.get_flattened_data())),format=fmt,method=method)
pairs={}
for mode in ('window','full'):
 previous=mode+'-before'
 for action in ('edge','arrow','drag'):
  current=mode+'-'+action
  if previous in images and current in images:
   a=images[previous].crop((5,40,635,430));b=images[current].crop((5,40,635,430))
   pairs[current]=dict(before=previous,after=current,roi=[5,40,635,430],pixels=630*390,changed=sum(x!=y for x,y in zip(a.get_flattened_data(),b.get_flattened_data())),bbox=ImageChops.difference(a,b).getbbox())
  previous=current
r=dict(structurally_valid=bool(rows),all_images_nonuniform=bool(rows) and all(v['unique_rgb']>1 for v in rows.values()),complete_case_matrix=all(mode+'-'+step in images for mode in ('window','full') for step in ('before','edge','arrow','drag')),captures=rows,comparisons=pairs,physical_access=True,console_writes=False,runner_sha256=hashlib.sha256(runner_bytes).hexdigest(),limits='Cold-read private GDI and game-produced images. Independently inspect landmarks and UI stages; changed pixels alone do not prove camera movement. No observed physical HDMI output, FPS or acceleration measurement.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(captures=len(rows),comparisons=pairs)))
