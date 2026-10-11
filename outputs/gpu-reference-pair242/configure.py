"""Finish new242 harness before freezing; old frozen bytes remain untouched."""
import json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-preserve-empty241'
for p in (old/'preserve001/artifacts').glob('before-*'):
 shutil.copyfile(p,k/'preserve001/artifacts'/p.name)
for name in ['fixture-preserve001.json','fixture-seed001.json']:
 p=k/name;d=json.loads(p.read_text(encoding='utf-8'))
 d['new_unique_runtime']='nt5-phase242-preserve001'
 d['emulator_source_changed_only']=['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c']
 d['paired_inventory']=True;p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
p=k/'trace.py';s=p.read_text(encoding='utf-8')
s=s.replace('from preservation import preconditions,preserve_tuple','from preservation import preconditions,preserve_tuple\nfrom schema import parse as inventory_tuple,qualify as inventory_qualify')
s=s.replace(" if case=='preserve001':capture('after-preservation')",''' if case=='preserve001':
  reply=cmd('qom-get '+path+' xwn-inventory242-report')
  paired=inventory_tuple(reply)
  row['paired_inventory_reply']=reply;row['paired_inventory']=paired;save()
  repeat=cmd('qom-get '+path+' xwn-inventory242-report')
  row['paired_inventory_immutable']=repeat==reply;save();assert repeat==reply
  row['paired_inventory_result']=inventory_qualify(paired,t);save()
  # No pmemsave: it dispatches GPU CPU-access callbacks and would change state.''')
assert "capture('after-preservation')" not in s
p.write_text(s,encoding='utf-8')
p=k/'freeze.py';s=p.read_text(encoding='utf-8').replace("k.parent/'gpu-preserve-entry240/emulator-frozen.json'","k.parent/'gpu-preserve-empty241/emulator-frozen.json'")
s=s.replace("['source','artifacts/inputs','artifacts/ram-source','artifacts/build001']","['source','artifacts/inputs','artifacts/ram-source','artifacts/build001','preserve001/artifacts']")
p.write_text(s,encoding='utf-8')
p=k/'test-consume.py';s=p.read_text(encoding='utf-8').replace("b['changed_sources']==['hw/xbox/nv2a/pfifo.c']","b['changed_sources']==['hw/xbox/nv2a/nv2a.c','hw/xbox/nv2a/nv2a_int.h','hw/xbox/nv2a/pgraph/gl/renderer.c']")
p.write_text(s,encoding='utf-8')
p=k/'audit-emulator.py';s=p.read_text(encoding='utf-8').replace("r['publication_limit']='241 pre-snapshot, optional bounded existing232 preservation and RAM captures at pinned Xromwell entry. Internal complete byte comparison is not reference retirement, native ownership or hardware qualification.'","r['publication_limit']='242 finite before/after inventory during actual halted preservation; CPU callback queues and GL bindings unobserved, no reference retirement/native ownership/physical qualification.'")
s=s.replace('Guest241 debugger preservation using corrected241 empty-FIFO consume and224 CPU manager.','Guest242 paired reference census using unchanged241 preservation/consume and224 CPU manager.')
p.write_text(s,encoding='utf-8')
p=k/'portable-offload.ps1';s=p.read_text(encoding='utf-8').replace('Closed237/238/239','Closed240/241');p.write_text(s,encoding='utf-8')
print('242 configured; no guest launched')
