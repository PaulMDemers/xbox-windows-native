"""Fresh owned diagnostic; never mutate or reuse closed169/172 evidence."""
import ast, json, shutil
from pathlib import Path
k = Path(__file__).resolve().parent
old = k.parent / 'video-process-lifecycle169'
assert not (k / 'Run.ps1').exists()
names = ['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py',
         'discover_kernel.py','freeze.py','gdi-probe.c','preflight.py','prepare.py',
         'Run.ps1','sample_analysis.py','supervise.py','timing-interface.json','build-review.json']
for name in names:
    data = (old/name).read_text(encoding='utf-8').replace('video-process-lifecycle169','video-installer-startup173').replace('vlife169','vstart173').replace('xwnvl169','xwnvs173')
    if name.endswith('.py'): ast.parse(data)
    (k/name).write_bytes(data.encode('utf-8'))
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe','umpnpmgr.dll']:
    shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
root = Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32')
for name in ['advapi32.dll','ntdll.dll']:
    shutil.copyfile(root/name,k/'artifacts'/name)
p=k/'prepare.py'
s=p.read_text();needle="    f['files']['F/winnt/system32/umpnpmgr.dll']=sha(caller)"
assert needle in s
s=s.replace(needle,needle+"\n    for label,meta in read(k/'sites.json')['binaries'].items():\n        p=ws/meta['path'];assert sha(p)==meta['sha256']\n        assert m.sha(rr['F'].read('winnt/system32/'+label))==meta['sha256'],label\n        f['files']['F/winnt/system32/'+label]=meta['sha256']")
ast.parse(s);p.write_bytes(s.encode())
print('Fresh173 host kit created; no guest launch or driver/settings change')
