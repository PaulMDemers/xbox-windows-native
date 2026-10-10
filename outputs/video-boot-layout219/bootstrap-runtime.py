"""Derive a unique ordinary219 workload from the frozen216 runner, no launch."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];parent=k.parent/'video-gpu-handoff216'
dest=k/'runtime-provenance.json';assert not dest.exists();rows={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['common.py','upload_analysis.py','runner_analysis.py','sample_analysis.py','dib_analysis.py','timing_analysis.py','window_analysis.py','text_analysis.py','interval_policy.py','boundary_analysis.py','typed-state.py','supervise-emulator.py','run-emulator.py','Run.ps1','Prepare.ps1','audit-emulator.py','prepare-emulator.py','Invoke-216.ps1']
for name in names:
    p=parent/name;text=p.read_text();target='Invoke-219.ps1' if name=='Invoke-216.ps1' else name
    text=text.replace('video-gpu-handoff216','video-boot-layout219').replace('gstate216','blayout219').replace('Invoke-216.ps1','Invoke-219.ps1')
    if name=='prepare-emulator.py':
        text=text.replace('xwng216a','xwnl219a').replace('xwng216b','xwnl219b')
        start=text.index("binary=k/'artifacts/build001'");end=text.index("startup=",start)
        text=text[:start]+"binary=k/'artifacts/build001'/case/'xboxbvid.dll';assert sha(binary)==review['binaries'][case]['sha256']\npath='Applications/XWNFBoot/loader/xboxbvid.dll';restore(rr['E'],path,binary.read_bytes())\nfiles['E/'+path]=sha(binary);protected['E/'+path]=sha(binary)\n"+text[end:]
        text=text.replace("gpu_submission=False,","gpu_submission=False,")
        text=text.replace("limits='Captured physical-core211 policy, HAL/FATX/bootvid/display unchanged. Only new216 observational snapshot and fresh helper/startup paths. Snapshot OFF/ON; not GPU, physical, dump or speed qualification.'",
            "limits='Captured physical-core211 policy; same HAL/FATX/miniport/display and helper workload. Only matched219 bootvid layout and new namespace/startup differ. No GPU operation or device policy change; ordinary display compatibility only.'")
    if name=='audit-emulator.py':
        start=text.index('from snapshot_trace import analyze as snapshot_trace')
        end=text.index('save(dest,r)',start)
        text=text[:start]+"r['gpu_transfer_qualified']=False\nr['limits']='Fresh219 matched bootvid writable layout with unchanged211 GDI workload and strict event/integrity gates. No runtime tail guard proof from this ordinary run alone; no GPU submission/cache handoff or physical qualification.'\n"+text[end:]
    p2=k/target;assert not p2.exists();p2.write_text(text)
    rows[target]=dict(parent_path=p.relative_to(ws).as_posix(),parent_sha256=sha(p),derived_sha256=sha(p2))
dest.write_text(json.dumps(dict(passed=True,files=rows,guest_launch=False,physical_access=False,
    changed_gate='Removed216-specific register-snapshot assertion because unchanged211 miniport has no216 snapshot hooks. All workload/event/cold gates retained.'),indent=2)+'\n')
print('Unique219 runtime kit derived; not launched')
