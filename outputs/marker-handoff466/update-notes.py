"""Record the completed diagnostic boundary, preserving older continuation entries."""
from pathlib import Path
K=Path(__file__).resolve().parent;N=K.parent/'engineering-notes'
current='''# Current: 465/466 bounded markers host- and emulator-validated; physical test next

Read entry-marker465 REPORT/DESIGN/host001 and marker-handoff466 REPORT/DESIGN/
NEXT/ERRATA/source-review002/final-review plus emu003 actual records. Original
physical launcher/startup/720p unchanged; no console access this turn. No boot
reliability fix or D3D result. Next is a watched LED/screen physical diagnostic
after fresh staging/readback and explicit recovery review; no hardware queued.

465 actual x86 core32 cases +32 immutable repeat checks. 466 actual assembled
wrapper57 cases and linked post-stack26 cases; privileged/kernel/file/SMBus/TSC
effects MODELED on host. Exact predecessor source/payload reconstructed. New
emu-only XBE C:/xwn466/build001/default.xbe 537170B SHA256
74a479078f378b8f02c54d4bd146765a7d860031116f636a3658a6616c2bedf5.
Two markers: before wrapper handoff, after original MOV ESP02800000. New owned
tail02680000 beyond BSS, inside existing1MiB copy; return026000f5. Stage1 reason12
on failure; stage2 CLI/HLT quarantine, physical recovery not yet qualified.

466emu003 scoped PASS:8 actual checkpoints, both records completed2 transactions,
4 status reads/9 writes each; actual loader02000000; original paging/stack/code
continuation observed, full EFLAGS/register preservation.13 private captures,
240 actual mutation/truncation negatives. All BPs removed/physicalmode0, orderly
host exit0/no fallback. Stopped before Windows; debugger timing not ordinaryboot.
Cold10GB virtualmapping/327680localbytes/546changed, strictFALSE. Allocation
276dirs6554files255dirclusters0errors/orphans;QCOW/EEPROMsame.5hives+3baseline
binaries byte-identical; no new hive semantic qualification. Final811frozeninput
checks/22totalmemorycaptures rehashed. Source seeds/backing chains unchanged.

Preserve466emu001 passiveFTPfailure before stage/SITE;002 firstmarkerPASS then
wrong fixed01000000BP timeout and unacknowledged BP removal. Both hostexit0,
clean allocation;002 later guestwork UNKNOWN. Its inherited audit stop label is
INVALID (ERRATA), not evidence Windows didnot run. review001 negative fixture
mistakenly unchanged timestamp word preserved;review002 corrects only testinput.
All runtime IDs consumed; never relaunch/recollect/parent. Fresh003 uses actual
allocated address and bounded asynchronous stop handling; no candidate rebuild.

All owned sessions closed: build/hosts complete, prepare90613/57707, runners
43949/53490/71661, tracers81452/88965/65496, failed001audit36512, otherchecks exit0.
New private artifacts on C:/xwn465 and C:/xwn466. C~25.99GB,E~21.50GB decimal;
retain20GiB projectedreserve. No backing moves. Previous pushed438eb4bf; this
closeout to be checked/exact-staged/committed/pushed. Historical untracked intact.

'''
status='''# Current: early boot markers validated in emulator; watched console test next

Both new checkpoints passed an owned emulator run: before the wrapper handoff
and after Xromwell installs its stack. The original loader and continuation were
observed with registers and flags preserved. Host tests cover bounded success,
timeout and refusal behavior. This adds diagnostic visibility, not a boot fix.

The emulator was closed cleanly and its FATX allocation audit passed. Five hives
and the original launcher/FATX/video files remained byte-identical. Two failed
controller attempts are retained separately. No physical console files changed.
The next test needs someone watching the console LED and screen; no launch is
queued. See [466 report](../marker-handoff466/REPORT.md) and
[next test requirements](../marker-handoff466/NEXT.md).

The latest physical E health scan remains463:722 directories,8063 files,
zero allocation errors/orphans/marked bad clusters and1.76GB free. 720p remains
the working display baseline. D3D inventory/device work follows boot diagnosis.

'''
for name,text in [('CONTINUATION.md',current),('STATUS.md',status)]:
 p=N/name;old=p.read_bytes();assert not old.startswith(text[:40].encode());p.write_bytes(text.encode()+old)
p=K.parents[1]/'.gitattributes';p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
