# Windows 2000 graphics ladder PC control

The six allowed cases completed successfully in one new Windows 2000 SP4 PC
control: GDI, DirectDraw 7 inventory with default/HEL/HAL requests, and explicit
RGB32 system-memory blits with default/HEL requests. All reported Windows 5.0
build 2195 and returned process exit 0. The unchanged public checker verified
129,024 source/destination bytes across the three pixel cases, including the
untouched destination border. These are memory readbacks, not screen captures.
402 mutations of the actual reports/readbacks were rejected.

The guest used 64 MiB, a Pentium III CPU model, legacy IDE and Cirrus display at
640x480x16, without a network device. Explicit RGB32 offscreen surfaces worked
despite the 16-bit desktop. HAL-requested inventory is not hardware acceleration
evidence; this test did not create HAL-only surfaces, a primary surface or a D3D
device. Preview was disabled. No visual, timing, Xbox or GPU result follows.

The fixture was a new private child of the closed clean-media404 SP4 NTFS
installation, not another installation from ISO. Its source hash remained
ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796.
Neither the parent nor any old runtime was launched again. Private files are
under `/home/paul/xbox-windows-native/graphics437-pc001` and
`graphics437-independent001`; the backing chain stays at its original paths.

The sample was exactly 436 build004, SHA256
09d355d8e55081433b62f94a2203cfa56bb23c4e6181f07f9b5087c7b6f3d050.
A separate no-CRT runner copied it from an immutable floppy, recorded each real
process exit, imposed a 45-second per-process wait and requested a normal guest
restart. QEMU exited 0 with no deadline, host quit, terminate or kill. The outer
owned runner had a ten-minute deadline. Resource and UI leases were used.

Cold inspection enumerated 6,475 files before and 6,495 after, with 308/309
directories. All 20 additions belong to the test directory. Existing Windows
DLL/EXE/SYS hashes remained unchanged; QCOW checks passed. Five hives have clean
headers and independent raw-value agreement. The inherited SOFTWARE DRM value
type 1028 remains unknown to the typed decoder. This is not complete typed
registry or NTFS allocation-bitmap qualification.

The legacy event record scan gained one EventLog 6006 and startup records, with
no new scanned warning/error. It can include inactive ring records. Guest RTC
interpretation is four hours ahead of host UTC; neither record-number order nor
these timestamps is a performance measurement. The runner's restart receipt and
QEMU's ordinary reboot exit are separate evidence of orderly closure.

An independent read-only NTFS-3G extraction agreed on all 30 selected files:
the 20 test files, five hives and five runtime DLLs. Its FUSE view was unmounted,
its process closed, and the disk remained unchanged. This selected agreement
does not resolve the known 423 compressed-file/uninitialized-tail differences
between readers or establish a full-disk logical-file oracle.

131 frozen host dependencies were rechecked. Controller compilation had no
warnings, and all 24 imports matched actual NT5 exports. Preserve the two early
cold-auditor dependency failures (Python Registry path, then native hivex loader
path), both before disk access. `cold003.py` supplies the explicit environment.
The first result reviewer incorrectly applied the sample decoder to the
controller's different schema; its failure is preserved, and review002 handles
the two schemas separately. No guest rerun or evidence rewrite was involved.

The dashboard was reachable during the subsequent read-only connection attempt
but rejected the previously supplied capitalized password. No physical writes
or launch occurred in 437; the user supplied the corrected lowercase password
for the separate 438 attempt. Existing 720p configuration is unchanged and the
1080i investigation remains paused.

Evidence: `runtime-review002.json`, `independent001.json`, `controls001.json`,
`ntfs-phase1.json`, the two cold audit records and `preflight001.json`.
