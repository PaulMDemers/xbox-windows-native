"""MIT. Compare private game images with independent passive display captures."""
import hashlib,json
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent
P=Path('C:/xwn574/pc001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Exclude toolbar, cursor, and the observed central screenshot notification.
roi=(5,280,635,430)
frames=[]
for p in sorted((P/'phase1').glob('auto-*.png')):
    im=Image.open(p)
    if im.size==(640,480):
        frames.append((p,list(im.convert('RGB').crop(roi).get_flattened_data())))
results={}
for p in sorted((P/'collection001').glob('*.shot')):
    pixels=list(Image.open(p).convert('RGB').crop(roi).get_flattened_data())
    scores=[]
    for f,actual in frames:
        # Allow RGB565 display quantization, at most eight per channel.
        wrong=sum(max(abs(a-b) for a,b in zip(x,y))>8 for x,y in zip(pixels,actual))
        scores.append((wrong,f))
    wrong,f=min(scores,key=lambda x:x[0])
    results[p.name]=dict(game_sha256=sha(p),passive_frame=f.name,
        passive_sha256=sha(f),pixels=len(pixels),outside_rgb_tolerance=wrong,
        matched=wrong==0)
out=K/'display-review001.json';assert not out.exists()
r=dict(roi=roi,rgb_channel_tolerance=8,results=results,
       passed=all(x['matched'] for x in results.values()),
       limitation='Region agreement proves sampled display content, not continuous scanout or FPS.')
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
assert r['passed']
