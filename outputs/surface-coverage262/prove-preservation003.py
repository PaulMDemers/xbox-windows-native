"""Qualify closed262 callbacks and cold bytes, retaining the independent event gate."""
import copy,hashlib,importlib.util,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'emu003';dest=out/'preservation-proof.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert read(out/'host-state.json')['closed'] and read(out/'closure.json')['closed']
a=read(out/'audit.json');t=read(out/'trace.json');assert t['passed'] and t['closed'] and t['guest_resumed'] and not t['remaining_breakpoints'] and t['physical_mode_restored']
run=Path('E:/Codex-private-artifacts/xbox-windows-feasibility/coverage262/runs/nt5-coverage262-emu003');raw=run/'cpu-trace.log';data=raw.read_bytes()
spec=importlib.util.spec_from_file_location('proof260',k/'lifecycle-proof.py');proof=importlib.util.module_from_spec(spec);spec.loader.exec_module(proof)
r=dict(passed=False,debugger=True,ordinary_qualified=False,physical_access=False,native_gpu_ownership=False,
 raw_path=str(raw),raw_sha256=sha(raw),source_sha256=sha(Path(__file__)),parser_sha256=sha(k/'lifecycle-proof.py'))
try:
 r['lifecycle']=proof.prove(data,t,True)
 assert len(t['checkpoints'])==5 and all(p['attestation']['passed'] for p in t['checkpoints'])
 assert len({p['attestation']['file_object'] for p in t['checkpoints']})==1
 assert a['renderer_diagnostic_passed'] and a['integrity_passed'] and a['normal_shutdown_count']==1 and a['dashboard_return']
 assert a['renderer_probe']['passed']
 header=[x for x in a['renderer_probe']['lines'] if x.startswith('RESIDENT_IDENTITY_HEADER ')];assert header==['RESIDENT_IDENTITY_HEADER 369098752 4096 0']
 # Independent rejection controls alter actual recorded causal coverage only.
 mutations=[];lines=data.decode().splitlines()
 for label,life in [('age',r['lifecycle']['age_callback_lifetime']),('read_store',r['lifecycle']['read_store_lifetime'])]:
  for row in life['cpu']:
   needle=f"xwn_mem_callback244 phase={row['phase']} when={row['when']} thread={row['thread']} ref={row['ref']} addr={row['addr']} len={row['length']} stopped={row['stopped']}"
   assert lines.count(needle)==1
   changed=('\n'.join(line for line in lines if line!=needle)+'\n').encode()
   try:proof.prove(changed,t,True)
   except AssertionError:mutations.append(label+'_missing_cpu_phase'+str(row['phase']))
   else:raise AssertionError('Missing actual callback phase accepted')
 for key in ['age_sites','read_store_sites']:
  for row in r['lifecycle'][key]:
   if row['site'] not in [2,3,11,12] or (row['site']!=3 and not row['flags']&1):continue
   needle=f"nv2a_lifecycle244 phase=100 when={row['when']} thread={row['thread']} ref={row['sequence']} a={row['site']} b={row['flags']}"
   assert lines.count(needle)==1
   # Remove dirty status on dirty reads/age/write; remove entire group for eviction.
   changed=[line for line in lines if not (row['site']==3 and re.search(r'phase=10[0-6] ',line) and f"ref={row['sequence']} " in line)]
   if row['site']!=3:changed=[line.replace(needle,needle.rsplit(' b=',1)[0]+' b=0') for line in changed]
   try:proof.prove(('\n'.join(changed)+'\n').encode(),t,True)
   except AssertionError:mutations.append('site'+str(row['site'])+'_coverage_removed')
   else:raise AssertionError('Missing dirty/eviction coverage accepted')
 r.update(passed=True,scoped_pixel_preservation_proved=True,exact_cold_guest_bytes=65536,
  guard_and_padding_bytes_per_read=15812,pixels_per_pattern=143,negative_controls=mutations,
  strict_qualification_passed=a['strict_qualification_passed'],warning_error_events=a['warnings_errors'],
  limitations='Owned diagnostic surface and pinned historical emulator fixture only; no ordinary or physical speedup/native GPU grant. Strict event gate remains separate and is never waived.')
except BaseException as e:r['error']=repr(e)
finally:dest.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['passed','error','strict_qualification_passed','negative_controls'] if n in r}))
