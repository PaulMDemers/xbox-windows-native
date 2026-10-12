# Physical video capability probe completed

The user authorized probing the connected Xbox on October 12, 2026. The one
inventory launch at 16:49:33 UTC returned to UnleashX; collection at 16:50:36 UTC
found a complete app-local log, all protected baseline hashes unchanged, and
exactly unchanged startup plus five registry hives. No Windows boot, display
mode change, EEPROM write, PCI write or GPU command submission was requested.

Actual hardware: kernel 1.0.4034.1, 16,384 physical pages (64 MiB), GPU revision
163, MCPX revision 178. The Conexant register-zero read succeeded with 0x61;
the Focus probe returned C0000185. Its accompanying value is invalid and is
ignored. Encoder identity does not establish an exact motherboard revision.

Encoder settings are 0x004F0101: NTSC-M, saved 480p/720p/1080i flags, but active
AV-pack code 1 (standard AV), not code 4 (HDTV/component). The SDK lists only
640x480 and 720x480 at 32-bit/60. Inherited valid dimensions are 720x480.
This confirms the current connection does not expose HD modes. An HDMI plug
or a TV displaying an upscaled 1080 signal would not establish native 1080i.
Physical testing needs a component/HDTV-capable Xbox connection and a display
accepting 1080i. No forced-HDTV override was applied.

The exact binary first completed a fresh standalone emulator smoke test: loaded
XBE header/text/checkpoint/caller pins and the 352-byte record matched, inventory
completed, breakpoint was removed and physical mode stayed off. The ISO's D:
is read-only, so log_ok=0 there is explicitly distinct from physical log_ok=1.
Host exited orderly with code 0. The strict emulator disk comparison remains
FALSE: one byte in reserved sector 1536 changed. Full 8 GiB map/65,536-byte
overlay comparison found filesystem bytes inherited unchanged; both QCOW
structures and EEPROM were unchanged/clean. No failure was waived.

Build001 uses pinned prebuilt nxdk libraries; all recorded SDK libraries/headers
and tools stayed unchanged. The single inherited linker export-section warning
was reviewed. Initial static checkpoint review expected another equivalent
register allocation and failed before any launch; original checker and failure
are preserved in prior-review001 and review-failure001.json. The corrected
review pins actual bytes and does not modify the binary.

The protected physical baseline remains FATX0101, display118/shared158 and
audio004. The probe and log remain only in E:/Applications/XWNVideo288. It is
not an automatic startup entry. No 0.2.0 tag has been created.
