# RGB32 key semantics: complete observation, keyed copies fail

Two actual Windows2000 SP4 processes (default and HEL) completed all twelve
operations and exited1 as expected for their pixel failures. Both used the
same new keyprobe binary0fcbc34e3d18339aa0f4a7bfe1d2e8852846a697469e7a591d97456863b3649c,
17,366 bytes,23 actual NT5 import matches. The controller has24 matching imports.
Both compiled without warnings; neither executable was run on the host.

All six plain RGB32 copies per backend passed, including clipped copies. All
source captures matched. All six keyed copies per backend failed. SetColorKey
and GetColorKey returned success and retained the complete requested key values.
All blits returned DD_OK, all layouts matched, and all final reference counts
were zero. The unchanged independent full-width oracle reports134 destination
pixel mismatches per backend:

| Key | Unclipped keyed mismatches | Clipped keyed mismatches |
|---|---:|---:|
| 0x000000 | 36 | 21 |
| 0xff0000 | 36 | 22 |
| 0x123456 | 12 | 7 |

Every captured destination pixel across both backends matches a model comparing
only the low16 source/key bits. This is stronger evidence than the earlier
zero-key/red-only example: nonzero keys and near-colors reproduce it without a
clipper. It is still a model of behavior, not a trace proving which runtime or
driver instruction implements it. No DLL/driver change or workaround installed.

The desktop remained640x480x16. Actual enumeration returned105 records followed
by termination, with depths4/8/16/24 and no32-bit mode. It includes640x480x24 at
60/72/75/85Hz. Enumeration alone does not qualify applying any of those modes.

The new launcher requires completed preflight before dispatch. Its actual
adapter passed59 host refusal checks with modeled Popen, including partial or
missing receipts, changed pins, stale/future timestamps, identity mismatches,
repeat dispatch and consumed failed spawn. This actual run admitted145 exact
dependencies after completed atomic preflight publication. The previous445
ordering failure remains unchanged and is not retrospectively qualified.

Both processes were bounded at90seconds. The guest requested a normal restart;
QEMU exited0 without deadline, host quit, terminate or kill. Cold audit:
6,485 files,309 directories,10 owned additions, five clean/raw-agreeing hives,
protected Windows binaries/parent/floppy unchanged, clean QCOW check and one
new EventLog6006. Independent read-only NTFS3G extraction matched20 files,
unmounted successfully and left the disk unchanged. All owned processes closed.

92,160 raw pixel bytes captured. Independent tests rejected11,416 mutations of
actual reports, source pixels, passing plain-stage destination pixels and lengths;
originals unchanged. All12 graphics verifier test groups passed. The exact145
preflight dependencies were read back and archived under the private
key-semantics446-inputs001 capsule. No proprietary pixels or binaries committed.

The public batch wrapper gained fresh-prefix/exit-receipt handling after the
compiler's initial wrapper copy; that earlier copy remains private and was never
used by the guest. The actual compiled C source and binary are unchanged. The
native controller independently launches/waits/writes exclusive exit receipts.

Scope is a diagnostic of owned RGB32 system-memory surfaces on this NT5 PC
fixture. It does not pass rung04 RGB32, qualify Xbox, prove scanout/GPU behavior,
or establish whole-system correctness. Full NTFS allocation ownership and the
inherited SOFTWARE DRM typed-value decode limitation remain outside this audit.

API references: [DDCOLORKEY](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/ns-ddraw-ddcolorkey)
defines equal low/high values as a single key;
[EnumDisplaySettings](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enumdisplaysettingsa)
defines the indexed mode inventory. Actual receipts are in runtime-review001.json,
launch-admission001.json, independent001.json and final-review.json.
