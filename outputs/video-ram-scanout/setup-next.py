"""Preserve failed diagnostic; prepare a new observer with live kernel discovery."""
from pathlib import Path
import json,shutil
p=Path(__file__).resolve().parent;k=p.parent/'video-ram-scanout2'
t=json.loads((p/'candidate001/trace.json').read_text());assert t['status']=='capture_incomplete' and t['guest_resumed'] and not t['armed_breakpoints_remaining']
k.mkdir(exist_ok=False)
for n in ['display','tests']:shutil.copytree(p/n,k/n)
for n in ['0108-ram-primary.patch','patch-review.json','build-report.json','source-verification.json','host-tests.json','tests-body.c','probe.c','pe-review.json']:
 shutil.copyfile(p/n,k/n)
(k/'candidate001/artifacts').mkdir(parents=True);(k/'artifacts').mkdir()
for n in ['candidate001/artifacts/xwnram.dll','candidate001/build.json','artifacts/probe.exe']:shutil.copyfile(p/n,k/n)
for n in ['atomic_json.py','audit.py','configuration.py','cold-map.py','preflight.py','Run.ps1','supervise.py','record-closure.py','common.py','prepare.py','review.py','mark-diagnostic.py','verify.py','trace.py']:
 s=(p/n).read_text().replace('video-ram-scanout','video-ram-scanout2').replace('nt5-vrscan-','nt5-vrscan2-')
 if n=='trace.py':
  s=s.replace("from atomic_json import write_json","from atomic_json import write_json\nfrom discover_kernel import discover")
  s=s.replace("if not loaded:\n   loaded=modules", "if not loaded:\n   K,discovery=discover(g.read,command(4594,'info registers'),pes['ntoskrnl.exe'],read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols'])\n   r['kernel_discovery']=discovery\n   loaded=modules")
  s=s.replace("Path(__file__),old/'sites.json'", "Path(__file__),k/'discover_kernel.py',k.parent/'native-windows-nt5-kernel/kernel-publics.json',old/'sites.json'")
 (k/n).write_text(s,newline='\n')
