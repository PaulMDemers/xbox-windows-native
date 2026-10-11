"""Classify captured ranges without confusing unknowns or emptiness with ownership."""
import copy,importlib.util,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'reference-test001.json';assert not dest.exists()
spec=importlib.util.spec_from_file_location('analysis238',k/'analyze-references.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
v=dict(context=[0]*20,current_fifo=[0]*14,fifo_when=1,current_pg_only=[0,2],renderer_valid=1,surface_truncated=0,wait_mask=0,surfaces=[])
checks=0
def run(value):
    global checks
    r=m.classify(value,64*1024**2);assert not r['producer_close_proved'] and not r['all_references_retired'] and not r['ownership_qualified'];checks+=3;return r
r=run(v);assert r['queue_parser_empty'] and not r['observed_preservation_obstacles'];checks+=1
for bit in range(18,32):
    q=copy.deepcopy(v);q['current_fifo'][6]=1<<bit;r=run(q);assert not r['queue_parser_empty'];checks+=1
for bit in range(18):
    q=copy.deepcopy(v);q['current_fifo'][6]=1<<bit;r=run(q);assert r['queue_parser_empty'];checks+=1
q=copy.deepcopy(v);q['current_fifo'][5]=4;assert not run(q)['queue_parser_empty'];checks+=1
q=copy.deepcopy(v);q['renderer_valid']=0;r=run(q);assert not r['surface_inventory_complete'] and r['color_binding_present'] is None;checks+=1
q=copy.deepcopy(v);q['surface_truncated']=1;assert not run(q)['surface_inventory_complete'];checks+=1
surface=[65536,65536,1024,256,64,33,1,1,0,99,0,64*1024**2]
q=copy.deepcopy(v);q['surfaces']=[surface];q['context'][18]=1;r=run(q);assert r['dirty_bytes']==65536 and r['retained_access_callbacks']==1 and r['color_binding_matches_in_list']==1 and not r['invalid_ranges'];checks+=1
q['surfaces'].append(surface.copy());assert run(q)['overlapping_ranges']==[[0,1]];checks+=1
for col,val in [(0,2**64-1),(1,0),(1,17*1024**2),(2,65536),(3,0),(4,0)]:
    q=copy.deepcopy(v);q['surfaces']=[surface.copy()];q['surfaces'][0][col]=val;assert run(q)['invalid_ranges']==[0];checks+=1
q=copy.deepcopy(v);q['surfaces']=[surface.copy(),surface.copy()];q['surfaces'][1][0]=131072;assert not run(q)['overlapping_ranges'];checks+=1
dest.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=hashlib.sha256((k/'analyze-references.py').read_bytes()).hexdigest(),guest_io=False),indent=2)+'\n',encoding='utf-8');print('238 reference classification checks',checks)
