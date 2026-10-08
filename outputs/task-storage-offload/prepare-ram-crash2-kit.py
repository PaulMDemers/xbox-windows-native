"""Fresh observer revision after the preserved fixed-image relocation failure."""
from pathlib import Path
import json
w=Path(__file__).resolve().parents[2];old=w/'outputs/video-ram-crash';k=w/'outputs/video-ram-crash2'
assert (old/'crash001/closure.json').exists();k.mkdir(exist_ok=False);(k/'artifacts').mkdir()
names=['common.py','prepare.py','preflight.py','Run.ps1','Invoke-Lba.ps1','supervise.py','trace.py','audit-crash.py','configuration.py','cold-map.py','record-closure.py','verify.py','verify-payload.py','verify-render.py','verify-ram.py','atomic_json.py','discover_kernel.py','modules.json','layouts.json','kernel-review.json','fatx-review.json','nvnet-review.json','atapi-review.json','address-review.json','video-sites.json','DESIGN.md','NEXT.md']
for n in names:(k/n).write_text((old/n).read_text().replace('video-ram-crash','video-ram-crash2'),encoding='utf-8')
for n in ['build-review.json','Build.ps1','review.py','probe.c','trigger.c']:(k/n).write_bytes((old/n).read_bytes())
for n in ['probe.exe','trigger.sys']:(k/'artifacts'/n).write_bytes((old/'artifacts'/n).read_bytes())
for n in ['trace.py','verify.py']:
 p=k/n;s=p.read_text().replace('p.DIRECTORY_ENTRY_BASERELOC',"getattr(p,'DIRECTORY_ENTRY_BASERELOC',[])").replace('pe.DIRECTORY_ENTRY_BASERELOC',"getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[])");p.write_text(s,encoding='utf-8')
p=k/'prepare.py';s=p.read_text().replace("case='crash001';", "assert read(k.parent/'video-ram-crash/failure-verification.json')['failure_preserved']\ncase='crash001';");p.write_text(s,encoding='utf-8')
print('New observer kit; no preparation or launch')
