"""Read-only admission for an interrupted owned upload; never resumes or launches."""
import hashlib,importlib.util,json
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('physical576',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
out=K/'recovery-probe002.json';assert not out.exists()
q=c.verify();st=c.read(K/'stage001.json');sup=c.read(K/'supervisor001-stage.json')
assert not st['completed'] and not st['temporary_hook_installed'] and sup['closed'] and sup['exit_code']==1 and not sup['deadline_reached']
assert not (K/'launch001.json').exists()
name=st['current_upload']['path'];assert st['writes'][-1]==name and name not in st['staged']
rel=name[len(c.KIT)+1:];expected=Path(q['files'][rel]['path']).read_bytes()
r=dict(started_utc=c.m.utc(),completed=False,read_only=True,remote_writes=[],launches=0,partial_path=name,source_sha256=c.m.sha(Path(__file__).read_bytes()),failed_stage_sha256=c.m.sha((K/'stage001.json').read_bytes()),failed_supervisor_sha256=c.m.sha((K/'supervisor001-stage.json').read_bytes()))
c.m.write_json(out,r)
with c.m.connect(timeout=10) as f:
 c.m.baseline(f,'720p');assert c.startup(f,False)==st['startup_listing']
 assert 'xwn575' not in {n.lower() for n in c.m.names(f,'/E')}
 assert c.m.get(f,c.HOOK,True) is None
 owner=c.m.get(f,c.KIT+'/owner.json');assert c.m.sha(owner)==st['staged'][c.KIT+'/owner.json']['sha256']
 r.update(dashboard_reachable=True,hook_absent=True,owner_exact=True)
c.m.write_json(out,r)
b=c.m.cold_pair(name,r,out);assert b is not None and 0<len(b)<=len(expected)
assert b==expected[:len(b)],'Partial upload is not an exact expected prefix'
folder=Path('C:/xwn576/stage-recovery002');assert not folder.exists();folder.mkdir()
p=folder/'partial-before.bin';p.write_bytes(b)
r.update(completed=True,ended_utc=c.m.utc(),partial_bytes=len(b),expected_bytes=len(expected),exact_prefix=True,partial_sha256=c.m.sha(b),private_partial_path=str(p),uncertain_append_repeated=False)
c.m.write_json(out,r);print(json.dumps({n:r[n] for n in ['completed','partial_bytes','expected_bytes','exact_prefix','hook_absent']}))
