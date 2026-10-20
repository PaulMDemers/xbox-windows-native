"""MIT. Preserve stopped read-only recovery; draft bounded batched verifier."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent
r=json.loads((K/'stage002.json').read_text());sup=json.loads((K/'supervisor002-stage.json').read_text())
assert not r['completed'] and not r['writes'] and not r['temporary_hook_installed'] and sup['closed'] and not sup['completed']
failure=dict(reason='Fresh connection per file was too slow for600second verification budget; deliberately stopped owned read-only child before hook/helper writes.',verified_entries=len(r['staged']),host_terminated=True,deadline_reached=False,remote_writes=r['writes'],hook_installed=False,launch_sent=False,supervisor='supervisor002-stage.json',next='New stage003 double-reads in batches of at most16files/session. At most two read attempts on recognized transport failures. No mutation retry.')
(K/'stage-failure002.json').write_text(json.dumps(failure,indent=2)+'\n')
s=(K/'controller002.py').read_text().replace('package002.json','package003.json').replace('stage002.json','stage003.json').replace('launch-preflight002.json','launch-preflight003.json')
s=s.replace('import importlib.util,json,shutil,sys,time','import importlib.util,json,shutil,sys,time\nfrom batch_read001 import verify_batch')
start=s.index('    deadline=time.monotonic()+600',s.index('def launch():'));end=s.index('    with m.connect(timeout=15) as f:',start)
s=s[:start]+"    verify_batch(m,{**st['before'],**st['staged']},rec,check,'verified')\n"+s[end:]
(K/'controller003.py').write_bytes(s.encode())
s=(K/'stage_recovery002.py').read_text().replace('controller002.py','controller003.py').replace('stage002.json','stage003.json').replace("c.P/'before2'","c.P/'before3'")
s=s.replace('import importlib.util,json,time','import importlib.util,json,time\nfrom batch_read001 import verify_batch')
start=s.index(" for name,row in q['files'].items():");end=s.index(' with m.connect(timeout=15) as f:',start)
s=s[:start]+" expected={c.KIT+'/'+name:row for name,row in q['files'].items() if name.startswith('game/')}\n verify_batch(m,expected,r,out,'staged')\n"+s[end:]
(K/'stage_recovery003.py').write_bytes(s.encode())
for name in ['supervise002.py','observe002.py']:
    s=(K/name).read_text().replace('controller002.py','controller003.py').replace('stage_recovery002.py','stage_recovery003.py').replace('supervisor002','supervisor003')
    (K/name.replace('002','003')).write_bytes(s.encode())
for a,b in [('audit003.py','audit004.py'),('registry_review003.py','registry_review004.py'),('user_hive_audit002.py','user_hive_audit003.py'),('welcome_review002.py','welcome_review003.py')]:
    (K/b).write_bytes((K/a).read_text().replace('stage002.json','stage003.json').encode())
for a,b in [('review_save001.py','review_save002.py'),('close001.py','close002.py')]:
    (K/b).write_bytes((K/a).read_text().replace('stage002.json','stage003.json').replace('package002.json','package003.json').replace('supervisor002-','supervisor003-').encode())
s=(K/'recovery_host001.py').read_text().replace('controller002.py','controller003.py').replace('stage_recovery002.py','stage_recovery003.py').replace('package002.json','package003.json').replace('recovery-host001.json','recovery-host002.json').replace("'recovery_host001.py'","'recovery_host002.py'")
s=s.replace(' def settimeout(self,n):', ' def close(self):pass\n def settimeout(self,n):')
(K/'recovery_host002.py').write_bytes(s.encode())
print('Drafted bounded16-file readback batches; no physical action')
