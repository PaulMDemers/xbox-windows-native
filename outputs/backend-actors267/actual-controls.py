"""Mutate the captured rows, never the saved raw observations."""
import copy,hashlib,importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'emu001'
sp=importlib.util.spec_from_file_location('analysis',k/'analyze-ledger.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
t=json.loads((out/'trace.json').read_text());assert t['passed'] and t['closed']
rows=m.base.load(out,t,'ledger');ui=m.base.load(out,t,'ui');assert m.inspect(rows,ui)['unknown_actor_work']==0
negative=[]
def fail(label,kind,index,value,which='ledger'):
    a=copy.deepcopy(rows);b=copy.deepcopy(ui)
    next(v for v in (a if which=='ledger' else b) if v[0]==kind)[index]=value
    try:m.inspect(a,b)
    except AssertionError:negative.append(label)
    else:raise AssertionError('Accepted '+label)
for label,kind,index,value in [
 ('unknown actor owner',50,1,0),('missing epoch',50,3,0),('invented actor state',50,4,9),
 ('missing acknowledged thread',50,5,0),('wrong actor type',50,6,3),('missing actual function',50,7,0),
 ('wrong current native context',51,4,0),('wrong current window',51,6,0),('no context match',51,7,0),
 ('indexed capacity overflow',52,3,1025),('invalid index',53,3,65536),
 ('draw FBO not restored',56,4,99999),('read FBO not restored',56,6,99999),
 ('unknown FBO attachment',55,3,0),('unknown attachment type',55,4,99999),
 ('VAO not restored',60,4,99999),('missing vertex index',59,3,99999),
 ('oversized program attachments',62,3,65),('null attached shader',63,4,0),
 ('unknown texture owner',4,2,99),('pending renderer state',16,6,1)]:fail(label,kind,index,value)
fail('wrong UI native context',65,1,0,'ui');fail('missing VGA surface',64,2,0,'ui')
for kind in [50,51,52,53,54,55,56,57,58,59,60,61,62,63]:
    a=copy.deepcopy(rows);a.remove(next(v for v in a if v[0]==kind))
    try:m.inspect(a,ui)
    except AssertionError:negative.append('missing kind '+str(kind))
    else:raise AssertionError(kind)
# A pending work record is retained as unknown, not magically upgraded to PASS.
a=copy.deepcopy(rows);next(v for v in a if v[0]==50)[4]=2
assert m.inspect(a,ui)['unknown_actor_work']==1
dest=out/'actual-controls.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,rejected_mutations=negative,pending_work_remains_unknown=True,
    trace_sha256=hashlib.sha256((out/'trace.json').read_bytes()).hexdigest(),
    physical_access=False,retirement_ready=False),indent=2)+'\n')
print(len(negative),'actual row mutations rejected; pending state retained as unknown')
