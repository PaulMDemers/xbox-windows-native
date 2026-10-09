"""Exact cold restoration check before any runtime; no fixture writes."""
from common import *
case=sys.argv[1];assert case in ['candidate001'];out=k/case
dest=out/'preflight.json';assert not dest.exists()
f=read(k/('fixture-'+case+'.json'));disk=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name']
assert sha(disk)==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
art=out/'artifacts';art.mkdir(exist_ok=True)
r=dict(case=case,physical_access=False,fixture_sha256=sha(disk),files=[],hives=[])
with ColdIO(disk) as io:
    rr=readers(io,disk)
    for name,digest in f['files'].items():
        v,path=name.split('/',1);actual=m.sha(rr[v].read(path));assert actual==digest,name
        if not path.startswith('winnt/system32/config/') and path not in [STARTUP,'winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:
            r['files'].append(dict(volume=v,path=path,sha256=actual))
    for name in HIVES:
        data=rr['F'].read('winnt/system32/config/'+name);p=art/('before-'+name);p.write_bytes(data)
        r['hives'].append(dict(name=name,**hive(p)))
    actual=rr['F'].read('winnt/system32/config/system')
    expected=k.parent/'device-unused-package179/candidate001/artifacts/after-system'
    assert actual==expected.read_bytes()
    assert rr['F'].read('winnt/system32/config/software')==(k.parent/'device-unused-package179/candidate001/artifacts/after-software').read_bytes()
    for p in ['xwnsr181/attempt.log','xwnsr181/gdi-baseline.txt','xwnrps02/attempt.log']:
        try:rr['F'].read(p)
        except KeyError:pass
        else:raise AssertionError('Stale one-shot output '+p)
r.update(passed=True,captured_system_exact=True,captured_software_exact=True,
         inherited_explicit_unused_policy=True,physical_device_policy_preserved=False,display_token='xwnown' if case=='candidate001' else 'framebuf',
         configured_geometry=[640,480,32,60],runtime_geometry_qualified=False,guest_launch=False,
         limits='Captured core and two hives on older r15 filesystem, not a whole-console clone; default/SAM/security are inherited emulator files and structurally checked.')
save(dest,r);print('Exact cold physical-core preflight:',case)
