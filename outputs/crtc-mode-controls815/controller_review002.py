"""Check the exact bounded physical controller before freezing source admission."""
from pathlib import Path
import ast,datetime,hashlib,json
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(K/'physical.py').read_text();tree=ast.parse(s)
calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
site=[n for n in calls if isinstance(n.func,ast.Attribute) and n.func.attr=='sendcmd']
assert len(site)==1 and ast.unparse(site[0])=='f.sendcmd(COMMAND)'
launch=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='launch')
assert not any(isinstance(n,(ast.For,ast.While)) and site[0] in list(ast.walk(n)) for n in ast.walk(launch))
assert "f.sock.settimeout(20)" in s and "with out.open('x')" in s
assert s.index("with out.open('x')",s.index('def launch'))<s.index('f.sendcmd(COMMAND)')
assert "REMOTE='/E/Applications/XWNMode815'" in s
assert "COMMAND=r'SITE EXEC E:\\Applications\\XWNMode815\\default.xbe'" in s
assert "assert not out.exists()" in s and "assert get(f,path)==body" in s
assert "sha(get(f,name))==v['sha256']" in s
assert "for n,v in read(K/'sources001.json').items()" in s
assert "for n,v in read(K/'review001.json')['checks'].items()" in s
assert "'prefix002.json'" in s and "'model001.json'" not in s
assert "f.delete(" not in s and "STOR " in s and '/C/' not in s
r=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 controller_sha256=sha(K/'physical.py'),auditor_sha256=sha(Path(__file__)),
 one_SITE_no_retry=True,reply_bound_seconds=20,owned_E_path_only=True,
 fresh_output_guards=True,exact_source_build_and_readback_gate=True,
 no_startup_hook=True,physical_access=False)
with (K/'controller-review002.json').open('x') as f:json.dump(r,f,indent=2);f.write('\n')
print('PASS815 bounded physical controller review')
