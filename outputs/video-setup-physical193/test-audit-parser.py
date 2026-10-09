"""Host replay of the exact new physical audit gate; no physical action or fabricated result."""
import ast,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'audit-parser-tests.json';assert not dest.exists()
p=k/'audit-physical.py';s=p.read_text(encoding='utf-8');start=s.index('lines=attempt.splitlines();');end=s.index('result.update(setup_gate_passed=',start);end=s.index('\n',end)
code=compile(ast.parse(s[start:end]),str(p),'exec')
idle=json.loads((k.parent/'video-setup-runtime191/idle001/audit.json').read_text())['logs']['attempt.log']
pending=json.loads((k.parent/'video-setup-fresh192/pending001/audit.json').read_text())['logs']['attempt.log']
cases=[('actual_idle',idle,True),('actual_pending_timeout',pending,False),('pending_then_idle',idle.replace('INSTALL_PREFLIGHT_RESULT 0','INSTALL_PREFLIGHT_RESULT 258\nINSTALL_PREFLIGHT_RESULT 0'),True),('short_idle',idle.replace('OBSERVED_MS 5145','OBSERVED_MS 4999'),False),('contradictory_elapsed',idle.replace('ELAPSED_MS 5145','ELAPSED_MS 100'),False),('at_deadline',idle.replace('ELAPSED_MS 5145','ELAPSED_MS 300000'),False),('unknown_query',idle.replace('PREFLIGHT_RESULT 0','PREFLIGHT_RESULT 42'),False),('probe_boundary_pending',idle.replace('INSTALL_BEFORE_SAMPLE 0','INSTALL_BEFORE_SAMPLE 258',1),False),('final_pending',idle.replace('INSTALL_FINAL_RESULT 0','INSTALL_FINAL_RESULT 258'),False),('truncated',idle.rsplit('NORMAL_RESTART_REQUEST',1)[0],False)]
rows=[]
for name,attempt,expected in cases:
 env=dict(attempt=attempt,result={});exec(code,env);actual=env['setup_gate_passed'];assert actual==expected,name;rows.append(dict(name=name,expected=expected,actual=actual))
dest.write_text(json.dumps(dict(passed=True,physical_access=False,source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),checks=rows,limits='Synthetic corruptions only validate production parser; only original captured logs are runtime evidence'),indent=2)+'\n')
print('Actual idle/pending and eight corrupted/transition gate records checked')
