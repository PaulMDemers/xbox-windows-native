"""Freeze the matched pair and runtime/audit sources before a single launch."""
import ast,datetime,shutil
from common import *
old=k.parent/'video-windows-timing156'
text=(old/'supervise.py').read_text(encoding='utf-8').replace('nt5-vtime156-','nt5-vphys162-').replace('time.monotonic()+900','time.monotonic()+420')
(k/'supervise.py').write_text(text,encoding='utf-8')
(k/'check-leases.ps1').write_text((old/'check-leases.ps1').read_text(encoding='utf-8').replace('nt5-vtime156-','nt5-vphys162-'),encoding='utf-8')
dest=k/'fixtures-ready.json';assert not dest.exists()
control,candidate=[read(k/('fixture-'+v+'.json')) for v in ['control001','candidate001']]
assert control['parents']==candidate['parents']
changes={name for name in set(control['files'])|set(candidate['files']) if control['files'].get(name)!=candidate['files'].get(name)}
assert changes=={'F/winnt/system32/config/system','F/winnt/system32/drivers/xboxvnt5.sys','F/winnt/system32/xwnown.dll','E/Applications/XWNFBoot/loader/xboxbvid.dll'},changes
for case in ['control001','candidate001']:assert read(k/case/'preflight.json')['passed']
pins=read(k/'frozen-inputs.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
for path in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/('fixture-'+v+'.json') for v in ['control001','candidate001']]+[k/v/'preflight.json' for v in ['control001','candidate001']]+[
    k.parent/'video-surface-history/Invoke-Exclusive.ps1',
    k.parent/'native-windows-paint-save/prepare-fixture.py',k.parent/'native-windows-fatx-runtime/bulk_fatx.py',
    k.parent/'fatx-mapped-eof/coldio.py',k.parent/'fatx-mapped-eof/allocation.py',
    k.parent/'native-windows-fatx-preflight/analyze.py',
    k.parent/'native-windows-physical-f/decode-legacy-events.py',k.parent/'gpu-reset-banner152/ftp_deadline.py']:
    pins[str(path.relative_to(ws)).replace('\\','/')]=sha(path)
    if path.suffix=='.py':ast.parse(path.read_text(encoding='utf-8'))
save(k/'frozen-inputs.json',pins)
for case in ['control001','candidate001']:
    source=k/case/'source';source.mkdir(exist_ok=False)
    for path in list(k.glob('*.py'))+list(k.glob('*.ps1'))+[k/'frozen-inputs.json',k/'DESIGN.md']:
        shutil.copyfile(path,source/path.name)
save(dest,dict(passed=True,frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    changed_paths=sorted(changes),same_parents=True,both_cold_preflighted=True,
    physical_writes=False,guest_launch=False,performance_qualified=False,
    control_strict_pass_required_before_candidate=True))
print('Both fresh preparations/preflights exact; runtime sources frozen')
