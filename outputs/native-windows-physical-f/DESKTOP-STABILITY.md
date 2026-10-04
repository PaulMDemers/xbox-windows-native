# Physical desktop milestone and remaining instability

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

Neither lead has been tied to the physical crash. No speculative filesystem
change has been deployed. Preserve raw events, SYSTEM and setupapi.log in the
ignored artifacts directory before any further experiment.

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
IO, hardware stability, or the normal miniport. No new physical upload/launch
was made. The emulator was stopped through the diagnostic harness and its
overlay retained; this was not a normal Windows shutdown or cold filesystem
integrity test.

Rebuild with Build-VideoDimensions.ps1. Run test-video-dimensions.py and
test-video-trace.py with --miniport artifacts/xboxvnt5-dimensions.sys and a
separate --output. prepare-dimensions-fixture.py constructs the small owned
delta; preserve its physical-framebuffer-pci-001.qcow2 and
physical-video-trace-001.qcow2 backing chain. Source, build, test and fixture
manifests are versioned; binaries and screenshots remain local.
