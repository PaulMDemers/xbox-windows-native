import graph_base,graph_extra
from decode import validate_graph
def inspect(g,u,allocations):

    validate_graph(g,1,allocations,False)

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

