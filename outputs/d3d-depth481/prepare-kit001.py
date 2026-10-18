"""Fresh matched physical depth kit; build requires completed PC480 evidence."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'d3d-texture478'
names=('build001.py','host001.py','test-wrapper.c','decode.py','refusal_decode.py','failure_marker.py','controller-host001.py','binary-review001.py','package001.py','physical.py','runner.c','review001.py','module-read001.py','closeout001.py','cold-review001.py','archive-inputs001.py')
for name in names:
 s=(old/name).read_text(encoding='utf-8')
 s=s.replace('0x47800101','0x48100101').replace("cookie='47800101'","cookie='48100101'")
 s=re.sub(r'(?<![0-9])478(?![0-9])','481',s)
 s=re.sub(r'(?<![0-9])479(?![0-9])','480',s)
 s=s.replace('0x38373458','0x31383458').replace('0x38373452','0x31383452')
 s=s.replace('d3d-texture','d3d-depth').replace('graphics_texture','graphics_depth').replace('ladder/texture','ladder/depth').replace('scoped_texture_passed','scoped_depth_passed').replace('actual_texture_controls','actual_depth_controls').replace('textures=[','depth_cases=[')
 s=s.replace('r08d','r08bd').replace('r08s','r08bs')
 s=s.replace('0cf77cd741d0f066ee5a3fc4ad10508f3e6d8cb962c8a89c90fc19d6ee832f91','00f6487c474420a2b84d60381d2915621c047e33eb2c3b27adc2c2ecd99c9d2f')
 if name=='review001.py':
  a=s.index('g.validate(');b=s.index('\n',a)
  s=s[:a]+"g.validate(raw,[(root/(name+'-'+suffix+'.bin')).read_bytes() for suffix in g.SUFFIXES],backend,int(code))"+s[b:]
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
s=(K.parent/'d3d-depth480/actual-controls001.py').read_text(encoding='utf-8')
a="c=json.loads((K/'ntfs-cold1-002.json').read_text());p=Path(c['private_path'])/'files/xwn480';rows=[]"
b="c=json.loads((K/'physical001-collection.json').read_text());p=Path(c['files']['/E/xwn481/runner.txt']['path']).parent;rows=[]"
assert a in s;s=s.replace(a,b);(K/'actual-controls001.py').write_text(s,encoding='utf-8',newline='\n')
with (W/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n/outputs/d3d-depth481/** -text whitespace=cr-at-eol\n/outputs/d3d-depth481/review001.py -text whitespace=cr-at-eol,-blank-at-eof\n')
