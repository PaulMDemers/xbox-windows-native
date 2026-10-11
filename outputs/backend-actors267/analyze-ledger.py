import importlib.util,json
from pathlib import Path
k=Path(__file__).resolve().parent
def module(name):
    sp=importlib.util.spec_from_file_location(name,k/(name+'.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
base=module('analyze-base');extra=module('analyze-extra')
def inspect(rows,ui):
    assert all(r[0] in set(range(1,19))|{30,31,32,33}|set(range(50,64)) for r in rows)
    assert all(r[0] in {30,31,32,33,40}|set(range(52,66)) for r in ui)
    r=base.inspect([v for v in rows if v[0]<50],[v for v in ui if v[0]<50])
    r['legacy_uninstrumented_handle_count']=r.pop('shader_actor_completion_unknown')
    r.update(extra.inspect(rows,ui))
    r['shader_actor_completion_unknown']=r['unknown_actor_work']
    r['blockers']=['No object disposal or context unbinding','No OS thread join acknowledgment',
        'UI retained names not revoked','Conservative guest scanout continues',
        'Guest cache/PTE aliases and native deferred release remain separate']
    return r
if __name__=='__main__':
    out=k/'emu001';dest=out/'ledger-analysis.json';assert not dest.exists()
    t=json.loads((out/'trace.json').read_text());assert t['passed']
    rows=base.load(out,t,'ledger');ui=base.load(out,t,'ui');r=inspect(rows,ui)
    report=base.numbers(t['final_report'])
    assert report['shader_jobs_unknown']==r['unknown_actor_work'] and report['accounting']==0
    assert report['bindings']==r['texture_bindings'] and report['retirement']==report['native_grant']==0
    r.update(physical_access=False,debugger_observation=True,ordinary_qualified=False)
    dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
