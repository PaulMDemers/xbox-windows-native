"""Independent ownership extension parser; completion is not thread joining."""
import collections

def inspect(rows,ui):
    by=collections.defaultdict(list)
    for r in rows:by[r[0]].append(r)
    actors=by[50]
    handles={r[1] for r in by[9] if r[6]}
    saves=[r for r in actors if r[6]==1];loaders=[r for r in actors if r[6]==2]
    assert len(loaders)==1 and len(saves)==len(handles)
    assert {r[1] for r in saves}==handles
    assert len({r[2] for r in actors})==len(actors)==len({r[3] for r in actors})
    assert all(r[1] and r[2] and 1<=r[3]<=65536 and r[4] in [1,2,3] and r[7] for r in actors)
    assert all((r[4]==1 and r[5]==0) or (r[4]>=2 and r[5]>0) for r in actors)
    contexts={r[1]:r for r in by[51]}
    assert len(by[51])==2 and set(contexts)=={1,2}
    assert all(r[2] and r[3]==r[4]!=0 and r[5]==r[6]!=0 and r[7]==1 for r in contexts.values())
    assert contexts[1][2]!=contexts[2][2] and contexts[1][3]!=contexts[2][3]
    fixed={r[1]:r[2] for r in by[7]}
    expected_fbos={(1,fixed[0]),(1,fixed[5]),(2,fixed[9])}
    expected_vaos={(1,fixed[4]),(1,fixed[6]),(2,fixed[10])}
    assert {(r[1],r[2]) for r in by[54]}==expected_fbos and len(by[54])==3
    assert {(r[1],r[2]) for r in by[57]}==expected_vaos and len(by[57])==3
    expected_programs={(1,r[3]) for r in by[9] if r[2]}|{(1,fixed[8]),(2,fixed[12])}
    assert {(r[1],r[2]) for r in by[61]}==expected_programs
    for group,roles in [(rows,{1,2}),(ui,{3})]:
        d=collections.defaultdict(list)
        for r in group:d[r[0]].append(r)
        limits={(r[1],r[2]):r[3] for r in d[52]}
        assert len(d[52])==len(roles)*2 and set(limits)=={(role,f) for role in roles for f in [0,1]}
        for (role,family),count in limits.items():
            assert 1<=count<=1024
            entries=[r for r in d[53] if r[1:3]==[role,family]]
            assert len(entries)==count and {r[3] for r in entries}==set(range(count))
            assert all((r[4]!=0 or r[5:7]==[0,0]) for r in entries)
        for kind,details,restore in [(54,55,56),(57,59,60)]:
            objects={(r[1],r[2]):r[3] for r in d[kind]}
            assert len(objects)==len(d[kind])
            assert all(v in [0,1] for v in objects.values())
            assert {(r[1],r[2]) for r in d[restore]}=={key for key,v in objects.items() if v}
            assert len(d[restore])==sum(objects.values())
            assert all((r[1],r[2]) in objects and objects[r[1],r[2]] for r in d[details])
            for r in d[restore]:
                assert r[3]==r[4]
                if kind==54:
                    assert r[5]==r[6] and 1<=r[7]<=64
                    entries=[v for v in d[55] if v[1:3]==r[1:3]]
                    assert len(entries)==r[7]+2
                    assert {v[3] for v in entries}==set(range(0x8ce0,0x8ce0+r[7]))|{0x8d00,0x8d20}
                    assert all(v[4] in [0,0x1702,0x8d41] and (v[4]!=0 or v[5]==0) for v in entries)
                else:
                    h=[v for v in d[58] if v[1:3]==r[1:3]];assert len(h)==1 and 1<=h[0][4]<=64
                    entries=[v for v in d[59] if v[1:3]==r[1:3]]
                    assert len(entries)==h[0][4] and {v[3] for v in entries}==set(range(h[0][4]))
        programs={(r[1],r[2]):r[3] for r in d[61]}
        assert len(programs)==len(d[61])
        assert all(v in [0,1] for v in programs.values())
        assert {(r[1],r[2]) for r in d[62]}=={key for key,v in programs.items() if v}
        for h in d[62]:
            assert 0<=h[3]<=64
            entries=[r for r in d[63] if r[1:3]==h[1:3]]
            assert len(entries)==h[3] and {r[3] for r in entries}==set(range(h[3])) and all(r[4] for r in entries)
    surface=[r for r in ui if r[0]==64];native=[r for r in ui if r[0]==65]
    assert len(surface)==len(native)==1
    s=surface[0];n=native[0]
    assert s[1] and s[2] and s[4]>0 and s[5]>0
    assert s[6]==n[1]==n[3]!=0 and s[7]==n[2]==n[4]!=0
    assert s[6] not in [v[3] for v in contexts.values()]
    return dict(actor_records=len(actors),original_work_returned=sum(r[4]==3 for r in actors),
        unknown_actor_work=sum(r[4]!=3 for r in actors),thread_join_proved=False,
        native_contexts={str(role):r[3] for role,r in contexts.items()},ui_context=s[6],
        vga_surface_identity=s[2],vga_surface_texture=s[3],
        scoped_indexed_binding_rows=sum(r[0]==53 for r in rows+ui),
        container_attachment_rows=sum(r[0] in [55,59,63] for r in rows+ui),
        scoped_reference_query_valid=True,retirement_ready=False,native_gpu_grant=False,
        limits=['Only GL4.0 uniform/transform-feedback indexed buffers queried',
                'Only pinned backend containers and current UI containers enumerated',
                'No disposal, thread joining, UI holder revocation or scanout release'])
