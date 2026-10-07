"""Create a fresh crash-only kit from immutable diagnostic helpers, before freezing."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'dump-map-trace'
for name in ['common.py','configuration.py','cold-map.py','atomic_json.py']:
    p=k/name;assert not p.exists();text=(old/name).read_text().replace('dump-map-trace','controlled-dump').replace('trace001','crash001');p.write_text(text)
for name in ['hal-review.json','fatx-review.json','layouts.json']:
    p=k/name;assert not p.exists();p.write_bytes((old/name).read_bytes())
r=(old/'Run.ps1').read_text().replace('dump-map-trace','controlled-dump').replace('trace001','crash001').replace('-StopOnBugcheck','-TraceDiskWrites').replace('-Seconds 1200','-Seconds 900')
(k/'Run.ps1').write_text(r)
