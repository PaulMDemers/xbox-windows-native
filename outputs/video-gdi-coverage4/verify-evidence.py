"""Check frozen inputs, closures and outcome reports without upgrading failures."""
from pathlib import Path
import hashlib,json,ast
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
names=['video-gdi-coverage','video-gdi-scanout','video-gdi-scanout2','video-gdi-scanout3','video-gdi-scanout4','video-gdi-coverage2','video-gdi-coverage3','video-gdi-coverage4','video-gdi-scanout5']
rows=[]
for name in names:
 kit=k.parent/name;out=kit/'candidate001';pre=read(out/'preflight.json');closure=read(out/'closure.json');audit=read(out/'audit.json');verification=read(kit/'verification.json');fixture=read(kit/'fixture-candidate001.json')
 for n,h in pre['sources'].items():assert sha(out/'source'/n)==h,(name,n)
 for p in list(kit.glob('*.py'))+list((out/'source').glob('*.py')):ast.parse(p.read_text(),filename=str(p))
 assert sha(Path(closure['private_disk']))==closure['private_disk_sha256']
 run=Path(closure['private_disk']).parent
 for n,h in closure['run_metadata_sha256'].items():assert sha(run/n)==h
 assert read(run/'cleanup.json')==closure['cleanup']
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/fixture['fixture_name'])==fixture['fixture_sha256']
 for row in fixture['parents']:
  p=Path(row['path'].replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'));assert sha(p)==row['sha256']
 assert sha(kit/'artifacts/probe.exe')==pre['probe_sha256']
 assert sha(out/'artifacts/xwnown.dll')==pre['display_sha256']=='ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440'
 assert not audit['physical_access'] and not closure['physical_access']
 if (out/'trace.json').exists():
  t=read(out/'trace.json');assert t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not t.get('resume_error')
 rows.append(dict(kit=name,strict_qualification=audit['strict_qualification_passed'],verification_passed=verification['passed'],debugger=audit['debugger'],explicit_ui_intervention=audit['explicit_ui_intervention'],normal_shutdown_count=audit['normal_shutdown_count'],cases=len(audit['protocol_details']['cases']),pins={n:sha(out/n) for n in ['preflight.json','closure.json','audit.json']},verification_sha256=sha(kit/'verification.json')))
r=dict(evidence_consistent=True,physical_qualified=False,driver_changed=False,attempts=rows,verifier_sha256=sha(Path(__file__)))
(k/'evidence-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
