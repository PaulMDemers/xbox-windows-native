"""Prepare new depth480 PC kit with bounded numeric token substitution."""
from pathlib import Path
import re,json,hashlib
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'d3d-texture479'
for name in ('build001.py','binary-review001.py','prepare001.py','cold002.py','preflight001.py','run001.py','login001.py','review001.py','independent001.py','module-review001.py','closeout001.py','runner.c','launch_gate.py','floppy_check.py','floppy-tests001.py'):
 s=(old/name).read_text(encoding='utf-8')
 if name not in ('launch_gate.py','floppy_check.py','floppy-tests001.py'):
  s=re.sub(r'(?<![0-9])479(?![0-9])','480',s).replace('texture480','depth480').replace('graphics_texture','graphics_depth').replace('ladder/texture','ladder/depth').replace("sample/'texture.exe'","sample/'depth.exe'").replace('r08d','r08bd').replace('r08s','r08bs')
  s=s.replace("/texture477-build001","/depth480-build001")
  s=s.replace('scoped_texture_passed','scoped_depth_passed').replace('offscreen clear/texture','offscreen depth/order controls').replace('Closed PC texture PASS','Closed PC depth PASS').replace('presentation, depth, blend','presentation, stencil, blend')
 if name=='review001.py':
  a=s.index("g.validate(raw,");b=s.index('\n except',a)
  s=s[:a]+"g.validate(raw,[(p/(name+'-'+suffix+'.bin')).read_bytes() for suffix in g.SUFFIXES],backend,code)"+s[b:]
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
(K/'inherited-gate-tests001.json').write_bytes((old/'inherited-gate-tests001.json').read_bytes())
