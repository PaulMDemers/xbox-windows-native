"""Finish generation after preserved001 anchor miss, before any build/deploy."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'d3d-triangle476'
failure=dict(failed_script='prepare-kit001.py',failure='review001.py int(code) anchor differed',
             shared_source_changed=False,built=False,physical_access=False,
             sha256=hashlib.sha256((K/'prepare-kit001.py').read_bytes()).hexdigest())
(K/'preparation-failure001.json').write_text(json.dumps(failure,indent=2)+'\n')
for name in ('review001.py','module-read001.py','closeout001.py','cold-review001.py'):
    p=K/name;assert not p.exists()
    s=(old/name).read_text(encoding='utf-8').replace('476','478').replace('474','477').replace('triangle','texture').replace('r07','r08')
    s=s.replace('eee41bde74531434f777b5b0bd98784d0e56d5e992c7d541c91fe5f05848be59','0cf77cd741d0f066ee5a3fc4ad10508f3e6d8cb962c8a89c90fc19d6ee832f91')
    if name=='review001.py':
        needle='backend,int(code))';assert s.count(needle)==1
        s=s.replace(needle,"(root/(name+'-source-before.bin')).read_bytes(),(root/(name+'-source-after.bin')).read_bytes(),backend,int(code))")
    p.write_text(s,encoding='utf-8',newline='\n')
s=(K.parent/'d3d-texture477/actual-controls001.py').read_text(encoding='utf-8')
needle="c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn477';rows=[]";assert needle in s
s=s.replace(needle,"c=json.loads((K/'physical001-collection.json').read_text());p=Path(c['files']['/E/xwn478/runner.txt']['path']).parent;rows=[]")
(K/'actual-controls001.py').write_text(s,encoding='utf-8',newline='\n')
with (W/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n/outputs/d3d-texture478/** -text whitespace=cr-at-eol\n/outputs/d3d-texture478/review001.py -text whitespace=cr-at-eol,-blank-at-eof\n')
