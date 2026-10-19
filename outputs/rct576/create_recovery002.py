"""New recovery sources; preserve the failed original stage and controller."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K/'controller001.py').read_text()
s=s.replace("    return q\n", "    a=read(K/'recovery-admission002.json');assert a['passed']\n    for n,h in a['pins'].items():assert m.sha((K/n).read_bytes())==h,n\n    return q\n",1)
start=s.index('def stage():');end=s.index('def launch():');s=s[:start]+s[end:]
s=s.replace("K/'stage001.json'","K/'stage002.json'").replace("('stage','launch','collect')","('launch','collect')")
p=K/'controller002.py';assert not p.exists();p.write_bytes(s.encode())
for source,dest in [('audit001.py','audit002.py'),('registry_review001.py','registry_review002.py')]:
 p=K/dest;assert not p.exists();p.write_bytes((K/source).read_text().replace("K/'stage001.json'","K/'stage002.json'").encode())
s=(K/'supervise001.py').read_text().replace('supervisor001','supervisor002').replace('stage=3600','stage=1200')
s=s.replace("str(K/'controller001.py')", "str(K/('recovery_stage002.py' if action=='stage' else 'controller002.py'))")
p=K/'supervise002.py';assert not p.exists();p.write_bytes(s.encode())
