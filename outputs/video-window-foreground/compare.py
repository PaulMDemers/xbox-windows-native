"""Compare closed ordinary native scene runs; never qualify elapsed-time speed."""
import copy,hashlib,json,statistics,sys
from pathlib import Path
from protocol import *
k=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def compare(a,b):
 assert a['passed'] and b['passed'] and a['ordinary_qualified'] and b['ordinary_qualified']
 assert a['profile_attribution_passed'] and b['profile_attribution_passed']
 assert a['font_source_sha256']==b['font_source_sha256']
 assert len(a['cases'])==len(b['cases'])==18 and len(a['observed_readbacks'])==len(b['observed_readbacks'])==36
 assert all(v['matched'] for r in [a,b] for v in r['observed_readbacks'])
 rows=[]
 for x,y in zip(a['cases'],b['cases']):
  assert x['index']==y['index'] and x['reference_hash']==y['reference_hash'] and x['paints']==y['paints']
  for phase in ['move','redraw']:
   u,v=x[phase],y[phase];assert u['callbacks']==v['callbacks']
   rows.append(dict(index=x['index'],phase=phase,old_bytes=u['upload_bytes'],new_bytes=v['upload_bytes'],old_uploads=u['uploads'],new_uploads=v['uploads'],callbacks=dict(zip(HOOKS,v['callbacks'])),old_ms=x[phase+'_ms'],new_ms=y[phase+'_ms']))
 return rows
if __name__=='__main__':
 dest=k/'pair-review.json';assert not dest.exists()
 a,b=[read(k/c/'verification.json') for c in ['control001','candidate001']]
 f,g=[read(k/('fixture-'+c+'.json')) for c in ['control001','candidate001']]
 assert f['parent_manifest_sha256']==g['parent_manifest_sha256'] and f['protected']==g['protected'] and f['preserved_hives']==g['preserved_hives'] and f['inherited_configuration']==g['inherited_configuration']
 assert [v for v in f['payloads'] if v['path']!='winnt/system32/xwnown.dll']==[v for v in g['payloads'] if v['path']!='winnt/system32/xwnown.dll']
 assert f['startup_sha256']==g['startup_sha256']
 rows=compare(a,b);totals={}
 for phase in ['move','redraw']:
  group=[r for r in rows if r['phase']==phase]
  totals[phase]={v:sum(r[v] for r in group) for v in ['old_bytes','new_bytes','old_uploads','new_uploads']}
  totals[phase]['old_median_ms']=statistics.median(r['old_ms'] for r in group);totals[phase]['new_median_ms']=statistics.median(r['new_ms'] for r in group)
 mutations=[]
 for name in ['pixels','callback','paint','strict_gate','font','readback']:
  changed=copy.deepcopy(b)
  if name=='pixels':changed['cases'][0]['reference_hash']^=1
  elif name=='callback':changed['cases'][0]['move']['callbacks'][0]+=1
  elif name=='paint':changed['cases'][0]['paints'][0]+=1
  elif name=='strict_gate':changed['passed']=False
  elif name=='font':changed['font_source_sha256']='changed'
  else:changed['observed_readbacks'][0]['matched']=False
  try:compare(a,changed)
  except AssertionError:mutations.append(name)
  else:raise AssertionError('Accepted '+name)
 protocol_mutations=[]
 data=(k/'candidate001/artifacts/result.log').read_bytes()
 for old,new in [(b'MOVE_API_PIXELS 1 0 ',b'MOVE_API_PIXELS 1 1 '),(b'REDRAW_API_PIXELS 1 0 ',b'REDRAW_API_PIXELS 0 0 '),(b'PARENT_ORIGIN 0 0 0',b'PARENT_ORIGIN 1 0 0'),(b'COMPLETE 0 18 ',b'COMPLETE 1 18 ')]:
  assert old in data
  assert not validate_log(data.replace(old,new,1))['passed'];protocol_mutations.append(old.decode())
 result=dict(passed=True,ordinary_emulator=True,physical=False,matched_parent_probe_and_callbacks=True,only_display_payload_differs=True,rows=rows,totals=totals,rejected_mutations=mutations,protocol_mutations=protocol_mutations,pins={c:sha(k/c/'verification.json') for c in ['control001','candidate001']},script_sha256=sha(Path(__file__)),timing_qualified=False,limits='Shared functional emulator resource; host preparation/cold audit activity can affect elapsed time. No timing speedup or physical FPS claim. Same rendered font source, exact live and cold pixels, native movement/repaint. No independent physical scanout/cursor pixel claim.')
 dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(totals,indent=2))
