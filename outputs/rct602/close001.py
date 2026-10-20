"""Close the observed PC game trace after cold and private visual checks."""
import datetime,hashlib,json
from collections import Counter
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn602/pc001/cold1-002/files/xwn602')
read=lambda n:json.loads((K/n).read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'final001.json';assert not out.exists()
r=read('review001.json');s=read('ntfs-phase1.json');t=read('trace-review001.json')
assert r['passed'] and s['closed'] and s['exit_code']==0 and t['passed']
assert not any(s.get(n) for n in ['host_quit','host_terminate','host_kill','space_stop','deadline'])
for n in ['binary-review001.json','media-review001.json','recorder-review001.json','setup-review001.json']:assert read(n)['passed']
visual=dict(passed=True,method='Assistant directly inspected all five original private640x480BMPs. Title and scenario list render; objective explicitly names Forest Frontiers. Options shows Window mode, edge scrolling checked and sound None. Final image shows unobstructed entrance, path and trees, MarchYear1,10000cash,0guests. This does not establish saved-scene equality, edge movement or FPS.',
 images={row['name']:sha(P/row['name']) for row in r['captures']})
(K/'visual-review001.json').write_text(json.dumps(visual,indent=2)+'\n',encoding='utf-8')
groups={}
for c in t['main_graphics_calls']:groups.setdefault(c['name'],[]).append(c)
assert t['total_pairs']==393 and t['main_pairs']==272 and t['other_pairs']==121
assert len(groups['StretchDIBits'])==32 and len(groups['CreateDIBSection'])==1
dib=groups['CreateDIBSection'][0];dd=groups['DirectDrawCreate'][0]
assert dib['result'] and dib['output_pointer'] and dd['result']==0 and dd['object'][0]==dd['output_pointer']
assert groups['IDirectDraw.Release'][0]['args'][0]==dd['output_pointer']
assert groups['IDirectDraw.Release'][0]['result']==0
assert not any(n in t['all_call_counts'] for n in ['IDirectDraw.SetCooperativeLevel','IDirectDraw.CreateSurface','IDirectDrawSurface.Blt'])
assert 'BitBlt' not in t['main_call_counts'] and t['all_call_counts']['BitBlt']==26
stretch=groups['StretchDIBits'];assert all(c['result'] not in [0,0xffffffff] for c in stretch)
assert all(c['args'][9]==dib['output_pointer'] and c['args'][11:]==[0,0xcc0020] for c in stretch)
drawing=dict(passed=True,total_pairs=393,main_pairs=272,other_pairs=121,
 main_counts=t['main_call_counts'],all_counts=t['all_call_counts'],
 stretch_results=dict(Counter(str(c['result']) for c in stretch)),
 stretch_destination_rectangles=[dict(rect=list(rect),count=count) for rect,count in Counter(tuple(c['args'][1:5]) for c in stretch).items()],
 dib_bits_pointer_matches_all_sampled_stretch_calls=True,stretch_rop_hex='00cc0020',stretch_usage=0,
 directdraw_created_and_released=True,sampled_limits=t['sampled_limits'],
 limits='PC windowed observation. CreateDIBSection header bytes were not captured, so DIB dimensions/bpp remain unmeasured.32 StretchDIBits calls are an early sample, not frames/FPS or park-specific coverage. Other DirectDraw interfaces/methods, GDI internals and physical GPU use are not covered. No cost/overhead measurement.')
(K/'drawing-review001.json').write_text(json.dumps(drawing,indent=2)+'\n',encoding='utf-8')
result=dict(closed=True,passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,
 owned_vm_closed=True,game_observation='Title and Forest Frontiers in Window mode under paired API recorder.',
 desktop=[1024,768],client=[640,480],drawing=drawing,registry_restored=True,normal_shutdown_delta=1,
 new_system_events=r['new_system_events'],capture_errors=s.get('capture_errors',[]),
 preserved_setup_issues='input-review002.md and setup-review001.json; rejected post-close screen command did not reopen VM.',
 console_state='Untouched; last dashboard with no owned hook.596 SOFTWARE cleanup remains cold-only.',
 limits='No matched pristine game control, measured overhead, exact saved-scene baseline, FPS or Xbox acceleration result.',
 pins={p.name:sha(p) for p in K.iterdir() if p.is_file()})
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('602 CLOSED:393 paired calls; actual main-image GDI DIB/StretchDIBits path observed')
