# Physical desktop milestone and remaining instability

Current follow-up, 5 October: candidate0088 storage has passed short, five-minute
and fifteen-minute physical tests with independent integrity audits. The first
physical Paint-dimensions trial reached the desktop; the user confirms Paint
opened without issues and the saved files are present. Drawing/save/reopen and
post-run integrity remain unverified. A later Save attempt froze Paint and then
the system; the user manually rebooted. This session is a failure. See `../native-windows-fatx-recovery/physical-paint.json`.
The following documents the earlier failure and emulator diagnosis.

Physical cycle010 reached the Windows 2000 desktop. Paul confirmed keyboard,
mouse, drive browsing, Notepad and Calculator. The startup probe/restart was
disabled. The passing file IO report belongs to cycle009, not this boot.
The exact traced miniport remains the physical baseline; the normal miniport
still has an unresolved physical B4 regression despite working in xemu.

Cycle010 then produced delayed-write warnings and STOP 0xA
IRQL_NOT_LESS_OR_EQUAL. The photograph reads parameters 1C, 2, 0, and apparently
82409167. The last address and its module attribution remain unconfirmed. No
crash dump was recovered. Do not infer a resolved kernel symbol from an assumed
load address. Dashboard FTP returned; only read-only collection followed.

## Recovered storage evidence

System event records 49 and 50 identify
`\Device\HarddiskVolume6\winnt\system32\SET1.tmp` (Windows C:, native Xbox F:).
Ftdisk event50 carries trailing status C000000D, STATUS_INVALID_PARAMETER.
The temporary file was absent in the later dashboard listing. Older records
in these logs include emulator history and are not new physical results.

The downloaded setupapi.log is 181,317 bytes. Its original 131,990-byte package
prefix matches exactly, but the appended portion contains binary data mixed
with new driver-installation messages. The original package contains no bytes
above 127; the downloaded log contains 6,782. This is evidence of corruption,
not evidence of a defective drive or of a specific driver bug yet.

Investigate FATX cached writes, truncation and cache-manager callbacks before
another physical desktop launch. Two source-review leads remain unproven:

- VfatWrite rejects paging writes extending beyond AllocationSize with the
  observed status. Capture offset, length and file sizes when reproducing
  temporary-file growth/truncation; do not simply suppress that error.
- The CcDeferWrite branch does not pin the caller's buffer before handing the
  request to a callback that directly dispatches it again. A forced-defer test
  with a different process address space should check this separately.

The deferred-buffer lead was subsequently demonstrated and fixed in0076.
Emulator stress improved, but physical cycle011 crashed during boot before
the helper started. See [cache follow-up](CACHE-STABILITY.md) for the paired
tests, physical failure and current installed state. Neither lead has been
tied conclusively to the physical crash. Raw evidence remains preserved.

## Paint: independent divide-by-zero fixed in candidate

Application DrWatson records 2 and 3 report mspaint.exe C0000094 at 0101E7D0.
Disassembly of the owned executable shows GetDeviceCaps(HORZSIZE=4) stored at
object+218, then `pixel_width * 1000 / physical_width`. ECX was zero at the
division. The miniport left XMillimeter and YMillimeter zero; framebuf passes
those fields into GDI.

Patch0075 supplies rounded 96-DPI fallback dimensions, explicitly not a
measurement of the connected monitor. At 1024x576 it reports 271x152 mm.
Candidate trace miniport SHA256:
`f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb`.
The physical trace driver 413098... was preserved unchanged.

Validation:

- Clean patch-series replay and reverse check passed (patch-check-0075.json).
- Compiled mode queries passed four geometries; the actual Paint instruction
  sequence faults with the old zero divisor and succeeds with the candidate.
- Existing compiled trace/PnP forwarding and failure-guard tests passed.
- Full ordinary xemu boot `nt5-physical-f-dimensions-extra-001`, using the
  128-plus-extra resource model and candidate HAL, launched Paint from startup.
  Paint remained visible in two captures. No debugger execution edits were used.

This validates Paint startup in the emulator, not saving images, general file
IO, hardware stability, or the normal miniport. No physical upload/launch
was made during that emulator validation. The emulator was stopped through the diagnostic harness and its
overlay retained; this was not a normal Windows shutdown or cold filesystem
integrity test.

Rebuild with Build-VideoDimensions.ps1. Run test-video-dimensions.py and
test-video-trace.py with --miniport artifacts/xboxvnt5-dimensions.sys and a
separate --output. prepare-dimensions-fixture.py constructs the small owned
delta; preserve its physical-framebuffer-pci-001.qcow2 and
physical-video-trace-001.qcow2 backing chain. Source, build, test and fixture
manifests are versioned; binaries and screenshots remain local.

## Physical manual trial after storage qualification

`native-windows-fatx-recovery/launch-paint.py` verifies the completed long-soak
qualification and current filesystem/HAL/video/launcher hashes before changing
only the trace video driver to the hash-pinned dimensions candidate. It retains
the prior video driver at `F:/winnt/system32/drivers/xboxvnt5.pre-dim` and preserves
local prelaunch logs. Trace storage is reset to its known seed, and the existing
no-op startup remains unchanged: no automatic Paint launch or timed restart.
The user can reopen the two previously saved files, then manually test Paint
startup, drawing, saving and reopening. The user now confirms physical Paint
startup without issues and saved-file presence. This is not yet a drawing/save/
reopen test or a post-run integrity result. See the recovery README for the
prepared postpaint collection and audit sequence.

### Paint save failure after successful physical startup

The user reports attempting to save froze Paint and then the system, followed
by manual reboot. Collection preserved unchanged driver/HAL hashes and no
new persisted delayed-write event. There is no clean EventLog stop, application
EVT is unchanged, and the video trace still contains only its reset seed.
The fault has not been localized to filesystem, display, or Save-dialog shell
processing. See the recovery `paint-event-review.json` and postpaint audits.

Post-run audit: 3,439 binaries, nine hives and full allocation scan passed.
The new desktop untitled.bmp is truncated by 48 KiB (393,270/442,422 bytes).
This establishes incomplete persistence during the failed save session, not
a failing I/O offset or a proven deadlock cause. Drivers were left unchanged.

See [Paint save reproduction](../native-windows-paint-save/README.md) for the
subsequent emulator tests with the exact combined storage/video candidates.
Saving and persistence are now tested separately from the earlier startup-only
check. The hardware hang remains an open issue; no speculative driver change
has been promoted from the emulator's bounded successes.
