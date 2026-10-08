"""Synthetic lifecycle parser and lifetime/extent consistency tests."""
import copy,hashlib,importlib.util,json
from pathlib import Path
from lifecycle import parse,MAX_BYTES
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('verify_lifecycle',k/'verify-lifecycle.py');v=importlib.util.module_from_spec(sp);sp.loader.exec_module(v)
data=b'''nv2a_pgraph_surface_create_color Create: [COLOR @ 0x03c64000 (640x480)] (ln) aa:0, clip:x=0,w=640,y=0,h=480,p=1280
nv2a_pgraph_surface_create_zeta  Create: [ZETA  @ 0x03000000 (640x480)] (ln) aa:0, clip:x=0,w=640,y=0,h=480,p=1280
nv2a_pgraph_surface_upload [RAM->GPU] COLOR (lin) surface @ 0x03c64000 (w=640,h=480,p=1280,bpp=2)
nv2a_pgraph_surface_download [GPU->RAM] COLOR (lin) surface @ 0x03c64000 (w=640,h=480,p=1280,bpp=2)
nv2a_pgraph_surface_evict_reason Evicting old surface @ 0x03000000
nv2a_pgraph_surface_evict_overlapping Evicting overlapping surface @ 0x03000000 (640x480,p=1280)
nv2a_pgraph_surface_invalidated 0x03000000
'''
events=parse(data);assert len(events)==7 and events[0]['pitch']==1280 and events[2]['bytes_per_pixel']==2
end=len(data);bounds=dict(before=end+1,after=end+2,first_marker=end+3)
windows=[dict(sample=0,start_offset=end+4,end_offset=end+200)]
samples=[dict(sample=0,destination=dict(rows=[dict(points=[dict(physical=0x3ca0000),dict(physical=0x3ca0007)])]))]
loader=lambda w:b'nv2a_pgraph_surface_cpu_write 0x03c64000+0x3c000\nnv2a_pgraph_surface_cpu_write 0x03c64000+0x3c004\n'
result=v.summarize(events,bounds,windows,samples,loader);assert result[0]['inferred_extent_bytes']==614400 and result[0]['created_before_launch_request']
rejected=0
for i in range(4):
 ev=copy.deepcopy(events)
 if i==0:ev=[e for e in ev if e['kind']!='create']
 elif i==1:ev.append(dict(kind='invalidated',base=0x3c64000,offset=end+3,end_offset=end+4))
 elif i==2:
  for e in ev:
   if e['base']==0x3c64000 and e['kind'] in ['upload','download']:e['pitch']=1
 elif i==3:ev[0]['height']=1
 try:v.summarize(ev,bounds,windows,samples,loader)
 except AssertionError:rejected+=1
 else:raise AssertionError('Invalid lifecycle accepted')
for d in [b'nv2a_pgraph_surface_upload malformed\n',b'x'*(MAX_BYTES+1)]:
 try:parse(d)
 except AssertionError:rejected+=1
 else:raise AssertionError('Invalid trace accepted')
r=dict(passed=True,synthetic_only=True,parsed_event_types=7,valid_lifetime_extent_cases=1,rejected_cases=rejected,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['lifecycle.py','verify-lifecycle.py','test-lifecycle.py']})
(k/'lifecycle-tests.json').write_text(json.dumps(r,indent=2)+'\n');print('Seven event formats, extent lifetime and six failure gates passed')
