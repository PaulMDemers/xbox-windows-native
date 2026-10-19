"""Fault tests derived from observed missing '=' and unchecked HMP response."""
import json
from pathlib import Path
from input_transport001 import plan,submit
class Q:
 def __init__(self,fail_at=None):self.calls=[];self.fail_at=fail_at
 def call(self,method,args):
  assert method=='human-monitor-command';self.calls.append(args['command-line'])
  return "unknown key: '='" if len(self.calls)==self.fail_at else ''
rows=[]
# Decode independently using the known command's keyboard sequence, not the encoder table.
command='D:\\RUN579.EXE /close=_Berkswin2kWelcomeApp_'
keys=plan(command);assert keys[command.index('=')]=='equal';assert keys[:3]==['shift-d','shift-semicolon','0x2b'];assert keys[-1]=='shift-minus'
q=Q();assert submit(q,command,pause=lambda _:None)==len(command);assert q.calls[command.index('=')]=='sendkey equal 40';rows.append('observed full command includes one explicit equals key')
for text in ['good?','good\n','good\t','good\u00e9']:
 q=Q()
 try:submit(q,text,pause=lambda _:None)
 except ValueError:pass
 else:raise AssertionError('unsupported input accepted')
 assert not q.calls;rows.append('unsupported suffix rejected before first key '+repr(text[-1]))
q=Q(fail_at=2)
try:submit(q,'abc',pause=lambda _:None)
except RuntimeError:pass
else:raise AssertionError('HMP error swallowed')
assert len(q.calls)==2;rows.append('HMP error stops before third key')
for hold in [0,5001]:
 q=Q()
 try:submit(q,'a',hold_ms=hold,pause=lambda _:None)
 except ValueError:pass
 else:raise AssertionError('hold accepted')
 assert not q.calls;rows.append('invalid hold rejected '+str(hold))
p=Path(__file__).with_name('input-transport-tests002.json');assert not p.exists();p.write_text(json.dumps(dict(passed=True,cases=rows,scope='Host transport validation/fault tests; no UI behavior or Xbox evidence.'),indent=2)+'\n');print(len(rows),'transport checks passed')
