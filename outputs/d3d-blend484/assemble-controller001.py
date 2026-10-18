"""Prepare a new PC alpha experiment; never run the inherited depth attempt."""
from pathlib import Path
import re
K=Path(__file__).resolve().parent
old=K.parent/'d3d-depth480'
names=['build001.py','binary-review001.py','prepare001.py','cold002.py','preflight001.py','run001.py','login001.py','review001.py','independent001.py','module-review001.py','closeout001.py','runner.c','actual-controls001.py']
for name in names:
    p=K/name
    assert not p.exists(),p
    s=(old/name).read_text()
    s=re.sub(r'(?<![0-9])480(?![0-9])','484',s)
    for a,b in [('depth484','blend484'),('graphics_depth','graphics_blend'),('ladder/depth','ladder/blend'),("'depth.exe'","'blend.exe'"),('r08bd','r08cd'),('r08bs','r08cs'),('scoped_depth_passed','scoped_blend_passed')]:
        s=s.replace(a,b)
    s=s.replace('lifecycle sample','alpha sample').replace('unchanged lifecycle build001','alpha sample build001').replace('NT5 lifecycle receipts','NT5 alpha receipts').replace('offscreen depth/order controls','offscreen diffuse alpha controls').replace('actual depth output','actual alpha output').replace('PC depth PASS','PC alpha PASS')
    if name=='actual-controls001.py':
        s=s.replace('range(120)','range(300)')
        a=s.index(' for frame in frames:\n');b=s.index(' for frame,suffix in zip',a)
        s=s[:a]+''' for frame in frames:
  for y in range(64):
   for x in (0,16,63):
    for channel in range(3):
     at=(y*64+x)*4+channel;frame[at]^=16
     try:g.pixels(*frames)
     except ValueError:n+=1
     else:raise AssertionError('actual pixel mutation accepted')
     frame[at]^=16
'''+s[b:]
    if name=='closeout001.py':
        s=s.replace('Exact sampling/raster edges, X byte, presentation, stencil, blend, performance, games and GPU unqualified','Exact raster edges, X byte, exact partial rounding, destination/texture alpha, depth-blend interaction, presentation, performance, games and GPU unqualified')
    p.write_text(s,encoding='utf-8',newline='\n')
for name in ['launch_gate.py','floppy_check.py','floppy-tests001.py','inherited-gate-tests001.json']:
    p=K/name;assert not p.exists();p.write_bytes((old/name).read_bytes())
print('Fresh 484 controller sources prepared; no fixture or executable run.')
