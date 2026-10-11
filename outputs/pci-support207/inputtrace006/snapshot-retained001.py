"""Bounded post-trace snapshot of earlier successful file objects; no owner inference."""
import ast,hashlib,json,sys,time
from pathlib import Path
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
k=Path(__file__).resolve().parent;out=k/'veto001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(k/'preflight001.json');run=read(out/'run.json');trace=read(out/'trace.json')
assert not run['closed'] and trace['status']=='both_class_failures_captured'
assert trace['guest_resumed'] and trace['breakpoints_remaining']==0
assert sha(k/'trace.py')==plan['sources']['trace.py']
tree=ast.parse((k/'trace.py').read_text())
# Reuse only reviewed definitions/imports; never execute the observer main body.
nodes=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))]
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(k/'trace.py'),'exec'))
K=plan['kernel_base_expected'];L=plan['layouts'];sites={K+v:n for n,v in plan['sites'].items()}
pes={n:pefile.PE(v['path']) for n,v in plan['providers'].items()};loaded=[];verified=set()
dest=out/'retained-snapshot001.json';assert not dest.exists()
r=dict(scope=__doc__,run_pid=run['pid'],trace_sha256=sha(out/'trace.json'),source_sha256=sha(Path(__file__)),runtime_pins=[],files=[],ordinary_qualified=False,physical_access=False,owner_proven=False)
g=None
try:
    r['started_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();monitor('stop');g=Remote();g.ask('qSupported');g.ask('?')
    pin(K+plan['sites']['open_enter'])
    for call in trace['calls']:
        if call.get('enable')!=1 or call.get('status')!=0 or call['identity']['image']!='csrss.exe':continue
        prior=call['file_after'];current=optional(file_info,prior['address'])
        r['files'].append(dict(call_id=call['id'],original_process_context=call['identity'],previous_file=prior,current_file=current,matching_type_device_and_context=all(current.get(n)==prior[n] for n in ('type','size','DeviceObject','FsContext','FsContext2'))))
except Exception as e:r['error']=repr(e)
finally:
    if g:
        try:g.send('c');r['guest_resumed']=True
        finally:g.s.close()
    else:monitor('cont');r['guest_resumed']=True
    r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r.get(n) for n in ('error','guest_resumed','files')},indent=2))
