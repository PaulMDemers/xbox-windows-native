"""Pair observed pre-download caller with common entry; no pixel-preservation inference."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;o=k/'preserve001';dest=o/'site-pairs.json';assert not dest.exists()
p=o/'site-observation.json';r=json.loads(p.read_text());pending={};pairs=[];unpaired=[]
for row in r['rows']:
 key=(row['thread'],row['surface'],row['callback'],row['address'],row['size'])
 if row['site'] in [1,2,3,4,5]:
  if key in pending:unpaired.append(pending[key])
  pending[key]=row
 elif row['site']==6:
  old=pending.pop(key,None)
  if old is None:unpaired.append(row);continue
  assert old['sequence']<row['sequence'] and old['when']<=row['when']
  pairs.append(dict(reason=old['reason'],before=old,common_entry=row,draw_dirty_before=bool(old['flags']&1),draw_dirty_at_entry=bool(row['flags']&1),pixel_correctness_proved=False))
result=dict(observation_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pairs=pairs,unpaired=unpaired+list(pending.values()),truncated_sites=r['truncated_sites'],physical_access=False,pixel_preservation_proved=False)
dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(pairs=len(pairs),dirty_before=sum(x['draw_dirty_before'] for x in pairs),dirty_at_entry=sum(x['draw_dirty_at_entry'] for x in pairs),unpaired=len(result['unpaired']),truncated_sites=result['truncated_sites']),indent=2))
