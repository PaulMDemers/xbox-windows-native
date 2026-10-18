"""Failure injection into actual trace cleanup body; remote operations modeled."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'host004.json';assert not out.exists()
tree=ast.parse((K/'trace001.py').read_text())
body=next(n for n in tree.body if isinstance(n,ast.Try)).finalbody
code=compile(ast.fix_missing_locations(ast.Module(body=body,type_ignores=[])),'actual-cleanup','exec')
class NoRun:
    def exists(self):return False
cases=0
for fail in range(1,8):
    events=[];active={0x11105,0x94aff};r={}
    def event(name):
        events.append(name)
        if len(events)==fail:raise OSError('modeled cleanup transport failure')
    class Socket:
        def close(self):event('close')
    class Remote:
        s=Socket()
        def ask(self,c):event(c);return '0' if c=='qqemu.PhyMemMode' else 'OK'
    def bp(a,add):event('remove');active.remove(a)
    env=dict(g=Remote(),stopped=False,physical_mode=True,active=active,r=r,
             mon=lambda c:event(c),bp=bp,save=lambda:None,utc=lambda:'modeled',RUN=NoRun())
    exec(code,env)
    assert 'cleanup_error' in r and len(events)==fail
    assert r['remaining_breakpoints']==sorted(active)
    assert r['physical_mode_remaining']==(fail<=3)
    cases+=1
r=dict(passed=True,actual_trace_cleanup_failure_paths=cases,transport_modeled=True,
       no_cleanup_success_fabricated=True,physical_access=False,
       source_sha256=hashlib.sha256((K/'trace001.py').read_bytes()).hexdigest())
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(r)
