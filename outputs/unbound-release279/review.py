"""Read-only eligibility review of CLOSED278; never changes its qualification."""
import hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'texture-boundary278'
sys.path.insert(0,str(old));import proof,graph_extra,graph_base
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(g,u,allocations):
    proof.validate_graph(g,1,allocations)
    # Complete independently checked inventories precede absence assertions.
    graph_base.inspect([r for r in g if r[0]<50],[r for r in u if r[0]<50])
    ext=graph_extra.inspect(g,u);assert ext['unknown_actor_work']==0
    integers={r[2]:r[3] for r in u if r[0]==31 and r[1]==3}
    for kind,names in [(54,{integers[0x8ca6],integers[0x8caa]}),(57,{integers[0x85b5]}),(61,{integers[0x8b8d]})]:
        headers=[r for r in u if r[0]==kind]
        assert len(headers)==len(names) and {r[2] for r in headers}==names

    units={r[1]:r for r in g if r[0]==3};bindings={r[1]:r for r in g if r[0]==4}
    accounts={r[1]:r for r in g if r[0]==5};selected=[]
    for i in range(4):
        a=units[i];b=bindings[a[2]];c=accounts[a[2]]
        assert a[3]==0 and b[2]==2 and b[4]==0x0de1 and c[2:5]==[2,1,1]
        name=b[3]
        assert not any(r[0]==32 and r[4]==name for r in g+u),'Bound selected texture'
        assert not any(r[0]==55 and r[4]==0x1702 and r[5]==name for r in g+u),'FBO selected texture'
        assert not any(r[0]==40 and name in r[3:6] for r in u),'UI selected texture'
        assert not any(r[0]==64 and r[3]==name for r in u),'VGA selected texture'
        selected.append(dict(unit=i,identity=a[2],gl_name=name,refs=b[2],cache=1,unit_edges=1))
    return dict(selected=selected,contexts=ext['native_contexts'],ui_context=ext['ui_context'],
                scope='Pinned GL4.0 queries and known renderer/UI containers, not every extension/object',release_authorized=False)
if __name__=='__main__':
    dest=k/'actual-edges.json';assert not dest.exists()
    out=old/'emu001';t=json.loads((out/'trace.json').read_text());assert json.loads((out/'host-closure.json').read_text())['closed']
    g=proof.load_pages(out,t,'initial',1,180000);u=proof.load_pages(out,t,'ui',1,8192)
    allocations=t['checkpoints'][0]['state_header'][10:14]
    result=inspect(g,u,allocations);rejected=0
    def reject(a,b):
        global rejected
        try:inspect(a,b,allocations)
        except (AssertionError,KeyError):rejected+=1
        else:raise AssertionError('Unsafe actual edge mutation accepted')
    for item in result['selected']:
        name=item['gl_name'];identity=item['identity']
        for group in (g,u):
            indices=[i for i,r in enumerate(group) if r[0]==32]
            # Every context role and every queried target family at its first unit.
            indices=[i for i in indices if group[i][2]==0]
            for i in indices:
                m=[r.copy() for r in group];m[i][4]=name
                reject(m,u) if group is g else reject(g,m)
            for i,r in enumerate(group):
                if r[0]==55:
                    m=[v.copy() for v in group];m[i][4:6]=[0x1702,name]
                    reject(m,u) if group is g else reject(g,m)
        for i,r in enumerate(u):
            if r[0]==40:
                for c in (3,4,5):m=[v.copy() for v in u];m[i][c]=name;reject(g,m)
            if r[0]==64:
                m=[v.copy() for v in u];m[i][3]=name;reject(g,m)
        for kind,column in [(3,3),(4,2),(5,3),(5,4)]:
            i=next(i for i,r in enumerate(g) if r[0]==kind and (r[2] if kind==3 else r[1])==identity)
            m=[r.copy() for r in g];m[i][column]+=1;reject(m,u)
    for group in (g,u):
        for kind in (30,32,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65):
            indices=[i for i,r in enumerate(group) if r[0]==kind]
            if indices:
                i=indices[0];m=group[:i]+group[i+1:]
                reject(m,u) if group is g else reject(g,m)
    result.update(actual_mutations_rejected=rejected,source_trace_sha256=sha(out/'trace.json'),
                  read_only=True,script_sha256=sha(Path(__file__)),strict_278_unchanged=False)
    dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
