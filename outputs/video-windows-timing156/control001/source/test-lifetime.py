"""Bound an initial watch's evidence before any later address reuse."""
import copy,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;target=k/'lifetime-tests.json';assert not target.exists()
spec=importlib.util.spec_from_file_location('series',k/'verify-series.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=0x03c64000
def row(kind,offset,**extra):return dict(kind=kind,offset=offset,end_offset=offset+1,base=base,**extra)
events=[row('create',0,binding='zeta',width=640,height=480,pitch=1280,normalized_layout='linear'),
        row('upload',1,bytes_per_pixel=2),row('download',3),row('evict_reason',4,reason='cpu-write'),row('invalidated',5),
        row('create',6,binding='zeta',width=640,height=480,pitch=1280,normalized_layout='linear'),row('download',7)]
r=m.lifetime(events,2);assert [e['offset'] for e in r['after_launch']]==[3,4,5]
checks=[]
for name,change in [('no_create',lambda e:e.pop(0)),('wrong_pitch',lambda e:e[0].update(pitch=2560)),
                    ('wrong_binding',lambda e:e[0].update(binding='color')),('no_upload',lambda e:e.pop(1)),
                    ('wrong_bpp',lambda e:e[1].update(bytes_per_pixel=4)),
                    ('invalidated_before_download',lambda e:e.insert(2,row('invalidated',1)))]:
    bad=copy.deepcopy(events);change(bad)
    try:m.lifetime(bad,2)
    except AssertionError:checks.append(name)
    else:raise AssertionError('Accepted '+name)
bad=copy.deepcopy(events);bad.pop(2) # A later generation's download must not qualify the initial watch.
try:m.lifetime(bad,2)
except AssertionError:checks.append('later_generation_download')
else:raise AssertionError('Address reuse escaped bound')
target.write_text(json.dumps(dict(passed=True,synthetic_only=True,rejected=checks,
    first_generation_bounded=True,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest()
    for n in ['lifecycle.py','verify-series.py','test-lifetime.py']}),indent=2)+'\n')
print(len(checks),'initial-watch lifetime gates passed')
