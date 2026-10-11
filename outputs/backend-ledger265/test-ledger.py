"""Independent decoder and edge/coverage mutations before any launch."""
import copy,importlib.util,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('ledger',k/'analyze-ledger.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
row=lambda *a:list(a)+[0]*(8-len(a))
rows=[row(2,10,1000,4096,256),row(4,1000,2,100,3553),row(5,1000,2,1,1)]
rows += [row(3,i,1000 if i==0 else 0) for i in range(4)]
rows += [row(6,100000+i,i+1,i<93) for i in range(51200)]
rows += [row(7,i,i+1) for i in range(14)]+[row(8,i,i+1) for i in range(16)]
rows += [row(10,0,100,1),row(15,1024,67108864),row(16),row(18)]
def context(c,thread):
 return [row(30,c,thread,33984,1,1)]+[row(31,c,i,0) for i in range(13)]+[row(32,c,0,i,0) for i in range(11)]+[row(33,c,0)]
rows += context(1,100)+context(2,100)
ui=[row(40,200,300,400,400,400)]+context(3,200)
r=m.inspect(rows,ui);assert r['collection_valid'] and not r['retirement_ready'] and r['shader_actor_completion_unknown']==1
checks=[]
def bad(name,change):
 a=copy.deepcopy(rows);b=copy.deepcopy(ui);change(a,b)
 try:m.inspect(a,b)
 except AssertionError:checks.append(name)
 else:raise AssertionError('Accepted mutation '+name)
bad('missing unit',lambda a,b:a.remove(next(x for x in a if x[0]==3)))
bad('duplicate unit',lambda a,b:a.append(next(x for x in a if x[0]==3)))
bad('unknown counted owner',lambda a,b:next(x for x in a if x[0]==4).__setitem__(2,3))
bad('missing cache edge',lambda a,b:a.remove(next(x for x in a if x[0]==2)))
bad('duplicate cache edge',lambda a,b:a.append(next(x for x in a if x[0]==2)))
bad('unknown unit-only binding',lambda a,b:next(x for x in a if x[0]==3).__setitem__(2,999))
bad('wrong context',lambda a,b:next(x for x in a if x[0]==30).__setitem__(1,3))
bad('wrong UI actor',lambda a,b:b[0].__setitem__(1,100))
bad('missing allocated buffer',lambda a,b:a.remove(next(x for x in a if x[0]==6)))
bad('duplicate buffer identity',lambda a,b:next(x for x in a if x[0]==6 and x[1]==100001).__setitem__(1,100000))
bad('pending state',lambda a,b:next(x for x in a if x[0]==16).__setitem__(6,1))
bad('missing texture context binding',lambda a,b:a.remove(next(x for x in a if x[0]==32)))
bad('mismatched callback inventories',lambda a,b:a.append(row(17,0,100,200,300,400,500,1)))
text='version=265 epoch=1 page=0 pages=1 rows=1 overflow=0 r0=1:2:3:4:5:6:7:8'
assert m.decode_pages([text],1)==[[1,2,3,4,5,6,7,8]]
for name,mut in [('stale epoch',text.replace('epoch=1','epoch=0')),('saturation',text.replace('overflow=0','overflow=1')),('missing page',text.replace('pages=1','pages=2')),('truncated row',text[:-2]),('duplicate row',text+' r0=1:2:3:4:5:6:7:8'),('missing row',text.split(' r0')[0])]:
 try:m.decode_pages([mut],1)
 except AssertionError:checks.append(name)
 else:raise AssertionError(name)
# Additional unit-only object is valid only with its complete matching record.
a=copy.deepcopy(rows);a += [row(4,2000,1,200,3553),row(5,2000,1,0,1)]
next(x for x in a if x[0]==3 and x[1]==1)[2]=2000
assert m.inspect(a,ui)['unit_only_bindings']==1
# Retained frontend names and an unknown shader actor are explicit blockers,
# even though an ownership observation itself can be structurally complete.
assert r['ui_hud_texture']==400 and r['ui_snapshot_texture']==400
assert not r['native_gpu_grant'] and len(r['blockers'])==5
p=k/'ledger-tests001.json';assert not p.exists()
p.write_text(json.dumps(dict(passed=True,negative_controls=checks,unit_only_positive=True,retirement_refused=True,physical_access=False,inputs={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['test-ledger.py','analyze-ledger.py']}),indent=2)+'\n')
print('265 independent parser:',len(checks),'negative controls and unit-only positive PASS')
