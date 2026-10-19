"""MIT. Seek passive display agreement including the screenshot-notice region."""
import hashlib,json,re
from pathlib import Path
from PIL import Image,ImageChops
K=Path(__file__).resolve().parent;P=Path('C:/xwn589/pc001')
out=K/'notification-review001.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
roi=(5,100,635,430) # Includes center notification, excludes toolbar/menu cursor.
frames=[]
for p in sorted((P/'phase1').glob('auto-*.png')):
    im=Image.open(p)
    if im.size==(640,480):frames.append((p,im.convert('RGB').crop(roi)))
assert 0<len(frames)<400
results={}
for p in sorted((P/'collection001').glob('*.shot')):
    expected=Image.open(p).convert('RGB').crop(roi);scores=[]
    for f,actual in frames:
        bands=ImageChops.difference(expected,actual).split()
        diff=ImageChops.lighter(ImageChops.lighter(bands[0],bands[1]),bands[2])
        wrong=sum(diff.histogram()[9:]);scores.append((wrong,f))
    minimum=min(n for n,_ in scores)
    matches=[dict(path=f.name,sha256=sha(f)) for n,f in scores if n==0]
    results[p.name]=dict(game_sha256=sha(p),minimum_outside_tolerance=minimum,
                         clear_region_matching_frames=matches)
runner=(P/'collection001/runner.txt').read_text()
begin=[int(n) for n in re.findall(r'^screenshot_settle_begin=(\d+)$',runner,re.M)]
end=[int(n) for n in re.findall(r'^screenshot_settle_end=(\d+)$',runner,re.M)]
assert len(begin)==len(end)==4
durations=[(e-b)&0xffffffff for b,e in zip(begin,end)]
r=dict(roi=roi,rgb_channel_tolerance=8,pixels=630*330,
       settling_ms=durations,results=results,
       passed=all(n>=10000 for n in durations) and all(v['clear_region_matching_frames'] for v in results.values()),
       limits='Image-content agreement includes the observed notification area. Matching frames alone do not assign guest input timing or prove continuous output.')
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));assert r['passed']
