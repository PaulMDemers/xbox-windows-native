# Paint save reproduction, 5 October 2026

The physical Paint save hang remains unresolved. The physical desktop BMP was
48 KiB short after a forced reboot; that persisted length does not identify a
blocked request. This kit reproduces the image size and exercises saving with
the same filesystem and dimensions miniport in private emulator overlays.
The initial tests used only the emulator. The subsequent hardware replay is
documented separately below; no driver replacement was performed for either.

## Pinned baseline

- Qualified emulator r15 checkpoint, SHA256
  `5298201608355fb4daec293cbf121993c4ff0b3896afd2b842b6508851a099cf`.
- Candidate0088 filesystem:
  `0ec6b5fdae65a1f85cba8c15021ba8095601d4462565b331329884526ff81336`.
- Dimensions trace miniport:
  `f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb`.
- Owned xemu resource-model executable:
  `969a99a83a308ba547ce3918015d676efee79912d97253d336bf8a35b5bc047d`,
  `XWN_NV2A_RESOURCE_MODEL=128-plus-extra`. Guest RAM remains 64 MiB.

`make-images.py` generates deterministic 24-bit BMPs: a scribble, white canvas,
coordinate pattern, and an odd-width coordinate pattern. The first three are
512x288 and 442,422 bytes, matching the physical file's declared dimensions and
length. The 513-pixel image additionally exercises scanline padding. These are
test patterns, not copies of the user's drawing.

## Completed actual Paint tests

`nt5-paint-save-003`: opened and saved the patterns, edited/saved a scribble,
and created/drew/saved a new default canvas. Five outputs survived a normal
Windows restart. Cold readback verifies complete BMP lengths, geometry and
pattern pixels; the two drawings contain non-white pixels. Both driver hashes
match. No hang or delayed-write event was observed. System records 47-52 retain
HID Input Service/Ftdisk errors and a rundll32 shutdown-time initialization
popup, followed by EventLog 6006. This is not an error-free system verdict.

`nt5-paint-pressure-001`: the bounded helper allocated/touched 16 MiB and held
it for 180 seconds. Its log reports 2,043,904 available physical bytes while
holding the allocation. The user pressed Enter to complete the fresh scribble
save, but that timestamp is unknown: overlap with memory pressure is not
established. A subsequent Save As ran with emulator disk throttling at 1 MiB/s
and 100 IOPS, returned normally, and was followed by normal Windows restart.
Both outputs are complete and byte-identical after restart. System records
47-51 contain HID Input Service/Ftdisk errors and normal EventLog stop; no new
delayed-write event. The throttle was restored before restarting.

The `*-save-audit.json` reports are targeted cold file/driver checks, not full
allocation, registry-hive or system-binary audits. Raw images, screenshots,
EVT files and command transcripts remain local under `artifacts` and
`work/runs`. Historical EVT records are retained and must not be attributed to
these boots. Guest time and host UTC are separate clocks.

## Diagnostic write replay

`replay.c` creates sixteen new BMP files without overwriting existing files.
Each writes a 54-byte header, six 64 KiB chunks and a final 48 KiB chunk,
flushes, closes and reopens the file, then compares every byte. Cases alternate
cached and write-through handles. The flushed log records case, step, value
and guest tick count around each write, flush and close. This sequence is a
diagnostic workload inspired by the partial file, not a captured Paint I/O
trace. Log flushing itself changes scheduling and can affect reproducibility.

`pressure.c` allocates at most 16 MiB, touches it for 180 seconds, frees it and
exits. Both helpers use ordinary Win32 file/memory APIs. Neither accesses raw
sectors, changes a driver, restarts Windows or overwrites existing test files.
They use CREATE_NEW; a repeated run on the same used overlay is unsupported.

`nt5-paint-replay-001` completed all sixteen cases under the 16 MiB helper
and disk throttling, then Windows restarted normally. The writer reported
434,176 available physical bytes before its first case. Its case interval was
guest ticks 159810-227790; the pressure process remained visible during the
replay and exited afterward. The memory helper completed 542 touch rounds.
All sixteen cold-read BMPs match the input byte-for-byte, including their
headers and final 48 KiB. The operation log has sixteen CASE_PASS entries and
final PASS, and both driver hashes match. System records 47-51 retain HID Input
Service/Ftdisk errors and normal EventLog stop; no delayed-write event. The
application EVT contains only the historical installer record. The emulator
was closed after dashboard FTP returned, and its disk was retained.

These tests did not reproduce the hardware hang. See `review.json` for the
bounded verdict and [NEXT-HARDWARE.md](NEXT-HARDWARE.md) for the diagnostic
and deployment requirements. At that checkpoint no physical test had launched.

## One-shot hardware replay follow-up

The user subsequently requested proceeding with the hardware diagnostic.
`runner.c` creates a flushed attempt log with CREATE_NEW, waits for the
unchanged replay executable, and requests a normal restart only after exit
zero. Failures leave Windows running with diagnostic logs; there is no blind
timer or forced restart. A persistent attempt log prevents automatic repetition
on subsequent Windows boots. `physical-replay.py collect` restores the original
no-op startup before retrieving reports and files.

`nt5-paint-runner-001` validated the exact launcher and writer, without Paint
or memory pressure. All sixteen files passed cold readback after its automatic
normal restart. Runner logs and system EventLog 6006 confirm that sequence;
HID Input Service/Ftdisk errors remain. `runner-emulator-validation.json` pins
inputs, launcher source/binary, screenshots and cleanup. This is separate from
the earlier manually restarted pressure run.

`physical-replay.json` records the single physical launch and subsequent state.
The deployment checks ownership, existing driver/HAL/launcher/loader hashes,
preserves pre-run logs and the user's partial BMP, and refuses an existing test
folder or launch record. Only the two helper executables, deterministic input,
trace seed and startup are written. No driver changes or repairs are included.
Physical collection, event review, native read-only allocation scan and
binary/hive audit are required before `qualify-physical.py` can pass.

### Physical result

One launch was accepted at 2026-10-05 16:38:54 UTC. The Xbox returned to the
dashboard without manual intervention; collection at 16:41:17 UTC restored the
no-op startup first. All sixteen 442,422-byte BMPs match the deterministic
source exactly. The writer completed in 27,000 guest milliseconds after its
startup delay. The attempt log records child exit zero and a normal restart
request. Filesystem, miniport, preserved old miniport, HAL, launcher, loader and
helper/input hashes match. The user's partial desktop BMP remains unchanged.

System records 90-95 contain normal EventLog start/stop and no new delayed-write
report. Ftdisk 49 and a shutdown-time rundll32 initialization popup remain;
there are no new application-log records. This is not an error-free-system
claim. The independent native read-only scan passed with 128,144 entries,
6,055 directories, 122,090 files, 6,060 directory clusters, zero allocation
errors and zero orphans. All 3,439 immutable binaries and nine registry hives
passed the separate post-reboot audit. `physical-replay-qualification.json`
records **PASS for this bounded workload**. The dashboard is running with
automatic startup disabled; no emulator or background test remains running.

The original physical Paint save hang is still unresolved. Actual Paint I/O
has now been traced in the emulator, as described below. The next physical
workload should use that observed sequence rather than the earlier 64 KiB replay.
`paint-write-target.json` identifies a hash-pinned MFC ordinal that calls
WriteFile and its argument layout. This is a static debugger target, not an
observed Paint save trace or fault attribution; verify the loaded module base
and bytes before setting breakpoints. Paint has no direct WriteFile import.

### Actual Paint file sequence

`nt5-paint-trace-001` saved the deterministic scribble using Paint's Save As
dialog. `trace-paint.py` observed Win32 entry/return pairs and MFC writes using
emulator breakpoints. It checked Paint PE header identity and executing DLL
bytes against the local references. This does not constitute a full live
module hash; breakpoints also perturb scheduling. No register changes or
forced API results were used.

The main CreateFileW call requests read/write access, share zero, OPEN_ALWAYS,
and FILE_ATTRIBUTE_NORMAL. Its security-attributes pointer is nonnull; the
pointee was not captured. Paint writes 14 bytes, then 40 bytes, queries its
current position (54), and writes twenty-seven 16,384-byte blocks. Every
WriteFile returned success with the full requested count. FlushFileBuffers,
SetEndOfFile and CloseHandle then returned success, in that order. The total
is 442,422 bytes. See `paint-sequence-review.json` and the full retained trace.

Two early tracer attempts failed on unavailable virtual memory (a DLL header,
then an instruction page before demand paging). Both removed their breakpoints
and resumed the guest. Their partial reports are retained separately; neither
is a guest crash. The final trace completed with no pending calls. The helper
now permits an unreadable header when executing bytes match, and steps past
an unmapped instruction stop so Windows can service its own page fault.

Paint returned from both saves. After a normal Windows restart, both BMPs
matched the input exactly and the filesystem/miniport hashes were unchanged.
System records 47-52 contain the existing HID/Ftdisk errors, a shutdown-time
rundll32 popup, and normal EventLog stop 6006; no new delayed-write report.
Application records remained unchanged. These are saved-file checks, not a
full emulator volume/hive audit. This Save As used a loaded deterministic image,
not the user's original fresh drawing.

### Replay of the observed sequence

`matched.c` preserves the earlier replay and instead uses 14 + 40 + 27*16384
byte writes, Paint's observed main open flags, a position query, flush, EOF,
and close. Files must first be CREATE_NEW-owned; it will not reopen an old
result. Sixteen cases alternate detailed logging with quiet target sequences.
Quiet cases issue no log/console I/O between target open and close. This still
does not reproduce Paint's heap layout, MFC exception paths, or GUI activity.

`Build-Matched.ps1` uses the pinned RosBE compiler with warnings as errors.
`matched-build-review.json` verifies imports against the pinned kernel32.
`prepare-matched.py` creates a new emulator child fixture and runs the tested
one-shot launcher with the new writer installed as its child `replay.exe`.
The existing physical helper, drivers and startup are untouched. Do not use
the old physical launch script to deploy this new workload; its completed
launch record and preserved outputs must remain intact.

`nt5-paint-matched-001` passed all sixteen cases without a debugger, additional
memory pressure, or an I/O throttle. All sixteen BMPs match the input exactly
after the launcher's normal restart. `qualify-matched.py` checks the cold audit,
29-write sequences in verbose cases, eight quiet cases, helper/source hashes,
driver hashes, event records, and cleanup. Records 47-53 show normal EventLog
stop with no new delayed-write event; HID/Ftdisk errors and two shutdown-time
rundll32 popups remain. The emulator is closed. This is a qualified emulator
workload, not a fix for the physical Paint hang.

## Reproduction and retained fixtures

Use the existing RosBE pin through `Build-Pressure.ps1` and `Build-Replay.ps1`.
Run fixture scripts under WSL Ubuntu, not Windows Python. `prepare-fixture.py`
requires the retained qualified r15 disk/backing chain, verifies its hash and
creates only new child images. `prepare-pressure.py` consumes the named fixture
from `fixture.json`; `prepare-replay.py` adds the replay helper to that clean
pressure fixture. Preparation asserts destinations do not already exist.

The actual corrected fixture is `paint-save-002.qcow2`, beside its parents in
`native-windows-fatx-forensics/artifacts`. Run001 failed before guest boot
because Windows could not open the long unnormalized backing chain. Run002
hit the expected trace-reuse guard before Paint. Copying the checkpoint beside
its parent and resetting the trace seed produced run003. These preparation
failures are not Paint failures. Fresh preparation now resets the trace seed.
Do not reuse a booted trace fixture without resetting it in a new child.

Launch the existing `native-windows-nt5-kernel/Invoke-Diagnostic.ps1` harness
with the pinned emulator, Complex_4627 BIOS, `f-boot-length-004.iso`, retained
r15 EEPROM, the prepared seed, ports 4594/4595/4596 and options ManualCapture,
StopOnCaptureComplete, RetainDisk, AllowGuestReboot, CompactTrace, UsbMouse.
Use localhost FTP through `launch_unleashx.py --port 4596` once the owned
dashboard is ready. No debugger execution edits are needed. HMP keyboard and
mouse commands drive the guest. Shut down through Windows, verify dashboard
return, then signal capture-complete so the harness closes the owned process.
The seed's relative backing path is intended for its copy under work/runs.

After cleanup, run `audit-saves.py --run RUN` under WSL. Decode copied EVT files
with `native-windows-physical-f/decode-legacy-events.py`. Preserve failures and
original fixtures; do not overwrite an earlier run directory.

Host space was reclaimed by round-trip-verified compression of one closed
owned CPU trace; `host-trace-compression.json` preserves the original hash.
No baseline disk or trace evidence was discarded.
