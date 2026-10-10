"""Restore unlaunched229 draft after a failed host formatting command."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;p=k.parent/'xemu-backend-reason228';dest=k/'draft-restoration.json';assert not dest.exists()
assert not (k/'emulator-frozen.json').exists() and not (k/'trace001').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old={n.name:sha(n) for n in k.iterdir() if n.is_file() and n.suffix in ['.py','.ps1','.md']}
pins=json.loads((k/'author.json').read_text())['parent_source_pins']
for name,digest in pins.items():
 source=p/name;assert sha(source)==digest
 text=source.read_text().replace('xemu-backend-reason228','xemu-backend-dashboard229').replace('reason228','dashboard229').replace('Invoke-228','Invoke-229')
 if name=='Run.ps1':
  text=text.replace('$PSScriptRoot artifacts/build002','$PSScriptRoot ../xemu-backend-reason228/artifacts/build002').replace('$PSScriptRoot build002.json','$PSScriptRoot ../xemu-backend-reason228/build002.json')
 if name=='run-emulator.py':
  text=text.replace("assert case in ['trace001']","assert case in ['trace001']\nassert os.environ.get('XWN_EMULATOR_FTP_USER') and os.environ.get('XWN_EMULATOR_FTP_PASSWORD'), 'Owned loopback credentials required BEFORE instance creation'")
  text=text.replace(" r.update(observer_exit_code=observer_code,", " if observer_code!=0:\n  r.update(observer_failed_before_collection=True);save()\n  (run/'capture-complete.signal').touch(exist_ok=False)\n r.update(observer_exit_code=observer_code,")
 if name=='audit-emulator.py':
  text=text.replace('Debugger228 exact refusal discriminator','Debugger229 pre-loader dashboard phase')
  text=text.replace("r['dashboard_return']=read(out/'launch.json')['cycles'][0].get('dashboard_return') is True", "r['dashboard_return']=(read(out/'launch.json')['cycles'][0].get('dashboard_return') is True) if (out/'launch.json').exists() else False\nr['windows_launch_record_exists']=(out/'launch.json').exists()")
  text=text.replace("r['backend_preservation_qualified']=r['preservation_trace_scope_passed'] and r['dirty_surface_coverage']", "r['publication_contract_qualified']=False\nr['backend_preservation_qualified']=False\nr['publication_limit']='Exact228 candidate report uses relaxed atomics; cross-host count/data publication unqualified. Earlier-phase observation only.'")
 if name=='trace.py':
  text=text.replace('One owned executable-pinned loader stop and opt-in backend preservation.','One owned pre-loader dashboard stop and compiled-model diagnostic.')
  start=text.index("iv=read(k.parent/'video-loader-handoff225/inventory002.json')");end=text.index('r=dict(scope=',start)
  text=text[:start]+'site=None # No guest breakpoint or native executing-code source pin.\n'+text[end:]
  start=text.index(' lock=acquire_monitor_lock(4594)');end=text.index(" r['before']=snapshot('before');save()",start)
  text=text[:start]+''' sys.path.insert(0,str(k.parent/'gpu-reset-banner152'))
 from ftp_deadline import DeadlineFTP
 import os
 with DeadlineFTP(time.monotonic()+6) as ftp:
  ftp.connect('127.0.0.1',4596,timeout=6)
  ftp.login(os.environ['XWN_EMULATOR_FTP_USER'],os.environ['XWN_EMULATOR_FTP_PASSWORD'])
  r['dashboard_barrier']=dict(utc=utc(),reply=ftp.sendcmd('NOOP'),physical_access=False)
 lock=acquire_monitor_lock(4594);cmd('stop');stopped=True
 g=Remote(4595);r['features']=g.ask('qSupported');r['initial_stop']=g.ask('?')
 r['prior_physical_mode']=g.ask('qemu.PhyMemMode');assert r['prior_physical_mode']=='0'
 assert g.ask('Qqemu.PhyMemMode:1')=='OK';r['physical_read_mode']=True
 r['observed_cpu_registers']=struct.unpack('<10I',bytes.fromhex(g.ask('g'))[:40])
 r['phase']='dashboard before only Windows launch; observed CPU registers, no native code source pin'
 path=qom_path(cmd('info qom-tree'));r['nv2a_qom_path']=path
 assert 'state=0' in cmd('qom-get '+path+' xwn-preserve227-report')
'''+text[end:]
  text=text.replace('  if stopped:\n   if armed:', '''  if stopped:
   if r.get('physical_read_mode'):
    try:r['physical_mode_restored']=g.ask('Qqemu.PhyMemMode:0')=='OK';r['physical_read_mode']=False
    except Exception as exc:r['physical_mode_restore_error']=repr(exc);quarantined=True
   if armed:''')
 if name=='supervise-emulator.py':
  start=text.index("while not (out/'trace-armed.signal').exists():");end=text.index("assert not (run/'cleanup.json').exists()",start)
  text=text[:start]+'''while not (out/'trace-finished.signal').exists():
    assert time.monotonic()<deadline and not (run/'cleanup.json').exists(),'Pre-loader phase not finished; no launch'
    time.sleep(.2)
trace=json.loads((out/'trace.json').read_text())
assert trace['closed'] and trace.get('guest_resumed') and not trace['remaining_breakpoints'] and trace.get('physical_mode_restored'), 'Unsafe diagnostic phase; no Windows launch'
'''+text[end:]
 target=k/('Invoke-229.ps1' if name=='Invoke-228.ps1' else name);target.write_text(text.rstrip()+'\n')
# Historical draft author/phase actions are superseded by this recorded recovery.
(k/'author.py').write_text('"""Historical author action already recorded in author.json; never rerun."""\nraise SystemExit("Read draft-restoration.json; current source restored before any freeze/launch")\n')
(k/'phase.py').write_text('"""Historical phase action already recorded; never rerun."""\nraise SystemExit("Read draft-restoration.json and current trace.py")\n')
for name in ['Wait-Prepare.ps1','Finish228-Prepare229.ps1']:
 (k/name).write_text("# Closed historical action; never replay collection or resource wait.\nthrow 'Read closure.json and NEXT.md; use direct unique preparation only'\n")
for name in ['DESIGN.md','REPORT.md','REVIEW-NOTES.md','NEXT.md']:
 (k/name).write_text('''#229 earlier dashboard phase: queued, unprepared

Uses exact228 build002 with unchanged native payload/policy and predicates.
One owned FTP barrier before SITE EXEC, paused physical RAMIN/tail reads,
same QOM diagnostic, physical GDB mode restored before safe resume. CPU registers
are observations, not a native executing-code source pin. No ownership grant.

No229 fixture/freeze/guest/Windows launch occurred.41 build lease refusals ended
19:48:27UTC October10; session1382 CLOSED1. PCI owns the HAL build lease; root did
not break it. All root227/228 guests are closed. Initial two preparation calls
were also refused before case creation. Preparation-resource.json retains exact
errors. Empty per-attempt console files carried no additional failure detail.

A host formatting command then accidentally emptied unlaunched draft sources.
No frozen input, compiled binary, fixture or completed227/228 evidence changed.
draft-restoration.json records the empty-file hashes and reconstruction from
the exact pinned228 parent. Historical author/phase byte pins remain retained;
they are superseded for current source. This is corrected, untested draft source.

Matched QEMU qatomic_read/set are relaxed; C11 host adapters do not qualify
cross-host report/data publication.229 explicitly forbids positive backend
qualification until a NEW release/acquire model build and appropriate tests.
Its possible dirty-surface observation alone cannot waive that gate. Native
reference retirement/allocator/context/alias contracts also remain unresolved.

Next inspect shared lease and actual stage records. Direct Prepare is allowed
only with absent229 case/seed/preparation identities. Do not rerun closed wait,
old author/phase or227/228 cases. Review current source, prepare once, cold audit,
freeze, supply loopback credentials in environment BEFORE run-emulator.py, and
launch once. No physical deployment; preserve0101/video0093,0088 and0.1.0.
''')
(k/'freeze.py').write_text('''"""Freeze unique229 source and exact228 compiled-byte inputs before launch."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'emulator-frozen.json';assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
pins=read(k.parent/'xemu-backend-reason228/emulator-frozen.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
f=read(k/'fixture-trace001.json');assert f['prepared'] and not f['inherited_null_policy'] and sha(Path(f['fixture_path_windows']))==f['seed_sha256']
for p in k.iterdir():
 if p.is_file() and p.suffix in ['.py','.ps1','.md','.json']:
  if p.suffix=='.py':ast.parse(p.read_text(),filename=str(p))
  pins[str(p.relative_to(ws)).replace('\\\\','/')]=sha(p)
assert 'credentials required BEFORE instance creation' in (k/'run-emulator.py').read_text()
dest.write_text(json.dumps(pins,indent=2)+'\\n');print('Frozen229 pins',len(pins))
''')
for p in k.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
dest.write_text(json.dumps(dict(passed=True,reason='host formatting failed Replace overload then wrote empty unlaunched draft files; restored pinned-parent derivation and current phase',before=old,after={n.name:sha(n) for n in k.iterdir() if n.is_file() and n.suffix in ['.py','.ps1','.md']},parent_source_pins=pins,fixture_created=False,frozen_inputs_changed=False,guest_launch=False,physical_access=False),indent=2)+'\n')
print('Unlaunched229 draft restored from pinned parent; syntax checked')
