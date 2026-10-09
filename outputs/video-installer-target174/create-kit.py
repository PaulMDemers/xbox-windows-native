"""New target-scoped observer; preserve173 bounded unreadable failure unchanged."""
import ast,hashlib,json,shutil
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'video-installer-startup173'
assert not (k/'Run.ps1').exists()
names=['atomic_json.py','audit.py','check-leases.ps1','close-emulator.py','common.py',
       'discover_kernel.py','freeze.py','gdi-probe.c','preflight.py','prepare.py','Run.ps1',
       'sample_analysis.py','supervise.py','timing-interface.json','build-review.json',
       'sites.json','site-disassembly.json','trace.py','verify-trace.py','test-pin-contract.py']
for name in names:
    data=(old/name).read_text(encoding='utf-8').replace('video-installer-startup173','video-installer-target174').replace('vstart173','vtarget174').replace('xwnvs173','xwnvt174')
    if name=='trace.py':
        needle="        try:\n            index=pin(site,who) if site else None"
        assert needle in data
        replacement="""        # Target-scope early loader and termination observations. No claim about
        # unrelated process startup and no nonresident pin waived for targets.
        if site and site['kind'] in ['loader_entry','terminate'] and who['image'].lower()!='rundll32.exe':
            r.setdefault('filtered_hits',[]).append(dict(address=a,site=site['name'],owner=who,reason='Outside declared rundll32 child scope'))
            assert len(r['filtered_hits'])<=1024
            remove(a);step();arm(a);save();continue
        try:
            index=pin(site,who) if site else None"""
        data=data.replace(needle,replacement)
    if name.endswith('.py'):ast.parse(data)
    (k/name).write_bytes(data.encode())
(k/'artifacts').mkdir(exist_ok=False)
for name in ['runner.exe','gdi-probe.exe','umpnpmgr.dll','advapi32.dll','ntdll.dll']:
    shutil.copyfile(old/'artifacts'/name,k/'artifacts'/name)
r=dict(parent_trace_source_sha256=hashlib.sha256((old/'trace.py').read_bytes()).hexdigest(),
       new_trace_source_sha256=hashlib.sha256((k/'trace.py').read_bytes()).hexdigest(),
       unreadable_bound_unchanged=32,hit_bound_unchanged=1024,wall_bound_unchanged_seconds=360,
       change='Loader entry/termination limited to rundll32 children BEFORE pin attempt; all skipped hits retained. Actual target unreadable sites remain unknown and bound is unchanged.',
       guest_launched=False,physical_access=False)
(k/'observer-scope-review.json').write_text(json.dumps(r,indent=2)+'\n')
print('New174 target scope, no guest launch; old173 source unchanged')
