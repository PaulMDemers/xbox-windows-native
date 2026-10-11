"""Describe proposed unit-release scope from real rows; perform no disposal."""
import importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'emu001'
sp=importlib.util.spec_from_file_location('analysis',k/'analyze-ledger.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
t=json.loads((out/'trace.json').read_text());rows=m.base.load(out,t,'ledger');ui=m.base.load(out,t,'ui')
r=m.inspect(rows,ui);assert r['unknown_actor_work']==0
bindings={v[1]:v for v in rows if v[0]==4};accounts={v[1]:v for v in rows if v[0]==5}
units=[v for v in rows if v[0]==3];assert len(units)==4 and all(v[2] and not v[3] for v in units)
entries=[]
for unit in units:
    b=bindings[unit[2]];a=accounts[unit[2]]
    assert a[2:5]==[2,1,1]
    gl_refs=[v for v in rows+ui if v[0]==32 and v[4]==b[3]]
    fbo_refs=[v for v in rows+ui if v[0]==55 and v[4]==0x1702 and v[5]==b[3]]
    entries.append(dict(unit=unit[1],binding_identity=b[1],gl_texture=b[3],gl_target=b[4],
        enabled=False,texture_dirty=bool(unit[4]),refs=2,cache_edges=1,unit_edges=1,
        context_texture_bindings=gl_refs,framebuffer_attachments=fbo_refs))
result=dict(observation_only=True,performed_release=False,units=entries,
    all_actors_original_work_returned=True,thread_join_proved=False,
    indexed_nonzero_buffers=[v for v in rows+ui if v[0]==53 and v[4]],
    ui_vga_texture=r['vga_surface_texture'],ui_stale_hud_name=r['ui_hud_texture'],
    ui_stale_snapshot_name=r['ui_snapshot_texture'],retirement_ready=False,
    requirements=['New isolated candidate, before/after immutable graph and exact input pins',
        'Call actual counted release only while refs==2/cache==1/unit==1; retain cache owner',
        'Resolve and unbind only matching target/unit in actual owning context, restoring active unit',
        'Set normal texture rebind state and prove resumed guest reuse and image contents',
        'Refuse unknown extra edges; never whole-finalize, join, delete cache objects or native GPU grant'])
dest=out/'release-evidence.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
