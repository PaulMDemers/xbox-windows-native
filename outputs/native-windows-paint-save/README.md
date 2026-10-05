# Paint save reproduction, 5 October 2026

The physical Paint save hang remains unresolved. The physical desktop BMP was
48 KiB short after a forced reboot; that persisted length does not identify a
blocked request. This kit reproduces the image size and exercises saving with
the same filesystem and dimensions miniport in private emulator overlays.
No physical Xbox access or driver replacement was performed for these tests.

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
bounded verdict and [NEXT-HARDWARE.md](NEXT-HARDWARE.md) for the next diagnostic
and deployment requirements. No physical test has been staged or launched here.

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
