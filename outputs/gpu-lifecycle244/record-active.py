"""Prepend exact active state and preserve old continuation bytes privately."""
import datetime,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];c=ws/'outputs/engineering-notes/CONTINUATION.md'
dest=k/'continuation-active001.json';assert not dest.exists()
old=c.read_bytes();p=k/'artifacts/continuation-before244.md';assert not p.exists();p.write_bytes(old)
prefix='''# Current:244 PREPARED; natural callback/display lifecycle diagnostic

Read outputs/gpu-lifecycle244/DESIGN.md/NEXT.md and actual build/attempt records.
New build004 observational hooks only; no native driver/policy/physical change.
Build001 property-anchor failure before compilation, build002 trace-format compile
failure retained/restored; build003 compiled but NEVER guest launched. Build004
uses atomic stopped-state observation and separate actual unlink/free events,
paired by CPU thread even across pointer reuse. ALL build processes CLOSED.
New preserve001 is authorized but inspect host-state/matrix/runner-start records
before deciding whether it has started; never replay/recollect a started case.
Its actors must fully teardown/resume/cold-audit under inherited bounds.
Observe actual callbacks, frontend glFinish/loan release and sync paths; no
disposal or native GPU grant. Emulator-only, no physical IO or peer merge.
Preserve0101/video0093,0088rollback,0.1.0,all failures and strict Ftdisk49 gate.
Closed234 build/portable offloaded with readback/original junction paths; no
backing chains moved. Keep20GiB guard and check actual projected capacity.

'''
c.write_bytes(prefix.encode('utf-8')+old)
dest.write_text(json.dumps(dict(recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),old_continuation_bytes=len(old),guest_start_not_asserted=True,physical_access=False),indent=2)+'\n')
