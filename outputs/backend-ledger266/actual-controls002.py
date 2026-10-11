"""Mutate the actual immutable ledger without changing original evidence."""
import copy,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'emu001';dest=out/'actual-controls002.json';assert not dest.exists()
sp=importlib.util.spec_from_file_location('ledger',k/'analyze-ledger.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
t=json.loads((out/'trace.json').read_text());rows=m.load(out,t,'ledger');ui=m.load(out,t,'ui')
original=m.inspect(rows,ui);assert original['collection_valid']
tests=[]
def reject(name,mutation):
    a=copy.deepcopy(rows);b=copy.deepcopy(ui);mutation(a,b)
    try:m.inspect(a,b)
    except AssertionError:tests.append(name)
    else:raise AssertionError('Actual mutation accepted: '+name)
first=lambda a,n:next(r for r in a if r[0]==n)
reject('missing counted unit',lambda a,b:a.remove(first(a,3)))
reject('duplicated counted unit',lambda a,b:a.append(first(a,3)))
reject('missing cache owner',lambda a,b:a.remove(first(a,2)))
reject('duplicated cache identity',lambda a,b:a.append(first(a,2)))
reject('unrecorded binding owner',lambda a,b:first(a,4).__setitem__(2,first(a,4)[2]+1))
reject('unknown unit binding',lambda a,b:first(a,3).__setitem__(2,1))
reject('missing buffer name',lambda a,b:a.remove(first(a,6)))
reject('wrong render context',lambda a,b:first(a,30).__setitem__(1,3))
reject('wrong UI actor acknowledgment',lambda a,b:first(b,40).__setitem__(1,first(a,30)[2]))
reject('pending state invented',lambda a,b:first(a,16).__setitem__(6,1))
reject('missing current texture binding',lambda a,b:a.remove(first(a,32)))
reject('missing vertex attribute binding',lambda a,b:a.remove(first(a,33)))
reject('missing shader actor record',lambda a,b:a.remove(first(a,10)))
reject('mismatched CPU callback inventory',lambda a,b:a.append([17,0,1,2,3,4,5,1]))
for kind in ['ledger','ui']:
    texts=[(out/v['file']).read_bytes().decode('utf-8') for v in t[kind+'_pages']]
    for label,mut in [('stale epoch',[texts[0].replace('epoch=1','epoch=0')]+texts[1:]),
                      ('overflow',[texts[0].replace('overflow=0','overflow=1')]+texts[1:]),
                      ('missing last page',texts[:-1])]:
        try:m.decode_pages(mut,180000 if kind=='ledger' else 8192)
        except AssertionError:tests.append(kind+' '+label)
        else:raise AssertionError(label)
bindings={r[1]:r for r in rows if r[0]==4}
unit_edges=[dict(unit=r[1],binding=r[2],refcount=bindings[r[2]][2],texture=bindings[r[2]][3],enabled=r[3]) for r in rows if r[0]==3 and r[2]]
display=next(r[2] for r in rows if r[0]==7 and r[1]==1)
uirow=next(r for r in ui if r[0]==40)
frontend=m.numbers(t['frontend_closed_report'])
assert uirow[3]==uirow[4]==uirow[5]==frontend['texture']
assert uirow[6]==frontend['fallback']==1 and frontend['live']==0
assert display!=uirow[3]
r=dict(passed=True,actual_negative_controls=tests,actual_mutations_rejected=len(tests),
    unit_edges=unit_edges,backend_display_texture=display,actual_ui_holders_match_backend_display=False,actual_ui_fallback=True,actual_ui_texture_live=False,actual_ui_texture=uirow[3],
    original_accounting_valid=True,retirement_ready=False,native_gpu_grant=False,
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    limits='Actual accounted owners and stale fallback UI names, not a demonstrated texture leak. Source destroys VGA fallback before this acknowledgment; live=0 confirms name is not currently a texture. Shader completion unknown. Original mistaken backend-alias analysis preserved separately.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
