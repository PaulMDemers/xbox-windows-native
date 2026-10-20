"""Test the evidence decision on artificial RGB data; no game-image alteration."""
import json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K.parents[1]/'work/python-packages'))
from PIL import Image
from scene_compare import compare,qualify
out=K/'scene-tests001.json';assert not out.exists()
a=Image.new('RGB',(640,480),(10,20,30));b=Image.new('RGB',(640,480),(90,80,70))
assert qualify(a,a,b,a,a)['passed']
negative={
 'no_camera_movement':qualify(a,a,a,a,a),
 'load_keeps_moved_view':qualify(a,a,b,b,b),
 'wrong_reference':qualify(b,a,b,a,a),
 'unstable_loaded_scene':qualify(a,a,b,a,b),
}
assert all(not r['passed'] for r in negative.values())
for im in [Image.new('RGB',(800,600)),Image.new('L',(640,480))]:
 try:compare(a,im)
 except AssertionError:pass
 else:raise AssertionError('invalid layout accepted')
c=a.copy();c.putpixel((160,80),(0,0,0));assert compare(a,c)['changed_pixels']==1
assert not qualify(a,a,b,c,c)['passed']
d=a.copy();d.putpixel((0,0),(0,0,0));assert compare(a,d)['exact']
out.write_text(json.dumps(dict(passed=True,positive=['restored scene','single pixel counted','UI outside ROI excluded'],rejections=list(negative)+['wrong frame size','wrong pixel mode','one wrong scenery pixel'],scope='Artificial RGB decision checks only; actual game review required.'),indent=2)+'\n')
print('Scene comparison: positive controls and seven rejection cases passed')
