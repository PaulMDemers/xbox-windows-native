"""Verify diagnostic captures/identities and retain failed ordinary gates."""
import datetime,hashlib,json,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'candidate001';run=Path('E:/xwn350/runs/nt5-primary350-candidate001');dest=K/'final-review.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sys.path.insert(0,str(W/'work/python-packages'));import pefile
frozen=read(out/'emulator-frozen.json')
for name,h in frozen.items():assert sha(W/name)==h,name
a=read(out/'audit.json');c=read(out/'closure.json');t=read(out/'trace.json');v=read(out/'trace-verification002.json')
assert c['closed'] and c['audit_sha256']==sha(out/'audit.json') and c['cleanup_sha256']==sha(run/'cleanup.json')
assert v['trace_sha256']==sha(out/'trace.json') and v['scoped_call_accounting_passed']
assert t['pending_calls']==0 and t['armed_breakpoints_remaining']==[] and t['guest_resumed'] and t['physical_mode_restored']
assert read(run/'host-exit.json')['passed'] and read(out/'launch.json')['cycles'][0]['dashboard_return']
assert a['integrity_passed'] and a['normal_shutdown_count']==1 and a['orderly_host_exit']
assert a['debugger'] and not a['ordinary_qualified'] and not a['performance_qualified']
assert not a['strict_qualification_passed'] and not a['scoped_combined_passed']
plan=read(K/'sites002.json');pes={}
for name,m in plan['modules'].items():assert sha(Path(m['path']))==m['sha256'];pes[name]=pefile.PE(m['path'])
for pin in t['pins']:
    name=pin['module'];p=pes[name];rva=pin['rva'];raw=bytes.fromhex(pin['raw']);resident=bytes.fromhex(pin['resident'])
    assert pin['source_sha256']==plan['modules'][name]['sha256'] and raw==p.get_data(rva,len(raw))
    assert len([m for m in t['loaded_modules'] if m['name']==name and m['base']==pin['base']])==1
    rel=[e.rva-rva for block in getattr(p,'DIRECTORY_ENTRY_BASERELOC',[]) for e in block.entries if e.type==3 and rva<=e.rva<rva+len(raw)]
    assert rel==pin['relocations'];expected=bytearray(raw)
    for pos in rel:struct.pack_into('<I',expected,pos,(struct.unpack_from('<I',expected,pos)[0]+pin['base']-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    assert bytes(expected)==resident
fixture=read(out/'fixture.json');assert sha(Path(fixture['fixture_path_windows']))==fixture['fixture_sha256']
captures={p.relative_to(out/'artifacts').as_posix():sha(p) for p in (out/'artifacts').rglob('*') if p.is_file()}
assert read(K/'protocol-tests001.json')['checks']==563 and v['actual_mutations_rejected']==549
failure=dict(original_freeze='freeze.py',sha256=sha(K/'freeze.py'),error="KeyError: E/winnt/system32/gdi32.dll",outcome='No freeze/guest launch occurred; explicit read-only prepared-provider hash check and freeze002 used before launch.')
r=dict(evidence_integrity_passed=True,scoped_call_accounting_passed=True,ordinary_qualified=False,performance_qualified=False,physical_qualified=False,strict_qualification_passed=False,original349_result_unchanged=True,frozen_inputs=len(frozen),runtime_pins=len(t['pins']),captures=captures,trace_sha256=sha(out/'trace.json'),audit_sha256=sha(out/'audit.json'),verification_sha256=sha(out/'trace-verification002.json'),fixture_sha256=fixture['fixture_sha256'],closed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),preflight_failure=failure,private_binaries_verified=list(pes),physical_access=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print('350 evidence closed:',len(frozen),'inputs,',len(t['pins']),'resident pins,',len(captures),'captures; no ordinary qualification')
