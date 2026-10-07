"""Check preserved diagnostic evidence and staged bytes; never infer coverage."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_text())
rows=[]
for kit,cases in [('fatx-install-buffer',['001','002','003']),('fatx-setup-buffer',['001'])]:
 root=k.parent/kit
 for case in cases:
  out=root/case;t=read(out/'trace.json');a=read(out/'buffer-analysis.json')
  source=out/'trace-source.py' if (out/'trace-source.py').exists() else root/'trace.py'
  assert sha(source.read_bytes())==t['source_sha256']
  assert sha((root/'sites.json').read_bytes())==t['sites_sha256']
  assert sha((out/'trace.json').read_bytes())==a['trace_sha256']
  for name,digest in a['evidence_sha256'].items():assert sha((out/name).read_bytes())==digest
  for stage in read(out/'collection.json')['stages'].values():
   assert sha((out/stage['output']).read_bytes())==stage['sha256']
  assert a['cold_checks_passed'] and not a['physical_qualified'] and not a['ordinary_qualified']
  assert not a.get('target_coverage',a.get('target_source_and_cold_coverage'))
  for e in t.get('events',t.get('records',[])):
   if not e.get('buffer_file'):continue
   data=(out/'artifacts'/e['buffer_file']).read_bytes()
   assert sha(data)==e.get('buffer_sha256',e.get('source_sha256')) and len(data)==e['length']
  if kit=='fatx-install-buffer':
   s=read(out/'trace-summary.json');assert s['private_trace_sha256']==a['trace_sha256']
   assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
  else:
   assert not t['records'] and not t['hit_counts'] and t['resume_error']
   assert not a['breakpoints_removed_before_disconnect']
  assert (ws/('work/runs/nt5-'+kit+'-'+case)/'cleanup.json').exists()
  rows.append(dict(kit=kit,case=case,cold_checks=True,target_coverage=False))
 checked=[]
 for rel in subprocess.check_output(['git','ls-files','--',root.relative_to(ws).as_posix()],cwd=ws,text=True).splitlines():
  assert subprocess.check_output(['git','show',':'+rel],cwd=ws)==(ws/rel).read_bytes(),rel
  checked.append(rel)
 assert checked, 'Stage kit before byte verification'
print(json.dumps(dict(evidence_verified=True,cases=rows,physical_qualified=False)))
