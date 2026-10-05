# Native Xbox Windows 2000 0.1.0

First preserved usable physical desktop milestone, 5 October 2026. This is an
experimental development release, not a claim of general stability. The source
tag is `v0.1.0`. The release deliberately retains filesystem candidate0088,
the dimensions/trace video miniport and the qualified physical HAL.

## What works

Windows 2000 SP4 runs natively on the 64 MiB Xbox. xemu is the separate PC
development environment. The installation is ordinary files on Xbox FATX F:,
which this Windows deployment calls C:. There is no NTFS container underneath
this physical installation. Do not confuse Windows drive letters with dashboard
letters, or with the separate NTFS emulator experiments.

Physical evidence includes boot video, desktop, keyboard/mouse, browsing,
Notepad, Calculator, Solitaire, Command Prompt, and two actual Paint saves and
reopens. Both Paint BMPs were independently downloaded and decoded after
restart. The five- and fifteen-minute storage trials passed, including mapped
file/truncate cases and cold payload verification. The latest independent full
F: allocation scan found zero errors/orphans across 128,171 entries; 3,439
Windows binaries and nine registry hives passed their separate audit.

The user additionally reports successful ping on the physical Windows desktop.
Record this as user-observed ICMP connectivity: target, direction, count and
latency were not captured. It does not yet qualify bulk TCP transfers or audio.
The user reports visibly slow window dragging, which is the next performance
target. These are observations, not benchmark measurements.

One previous physical Paint save froze the machine. It has not repeated in the
subsequent two manual saves or bounded replay tests. Its cause is unknown; this
release does not claim a demonstrated fix for that incident.

## Evidence and bundles

- [Manual Paint qualification](../native-windows-paint-save/physical-paint-repeat-qualification.json)
- [Matched physical replay](../native-windows-paint-save/physical-matched-qualification.json)
- [Fifteen-minute soak](../native-windows-fatx-recovery/physical-long-qualification.json)
- [Post-Paint binary/hive audit](../native-windows-fatx-recovery/postpaintrepeat-audit.json)
- [Capture summary](capture-summary.json), generated only on successful archive verification.
- [Recovery instructions](RECOVERY.md)
- [Engineering handoff](../engineering-notes/README.md) and [next development plan](../video-next/PLAN.md)

Local archives live at `E:/Codex-archive/xbox-windows-native/0.1.0` on the PC:

1. `xwn-0.1.0-physical-system.zip`: installed Windows, profiles, Program Files,
   owned test directories and F-root evidence. Pagefile, games and unrelated
   applications are excluded. Empty captured directories are retained.
2. `xwn-0.1.0-boot-dashboard.zip`: the exact boot application and a pre-menu-edit
   dashboard/config recovery copy. This is private recovery material.
3. Source/evidence archive and Git bundle at the tagged revision, with a separate
   manifest recording their hashes. Raw Windows binaries, dashboard binaries,
   user profiles, firmware and credentials are not published to GitHub.

The physical snapshot is read while Windows is stopped and UnleashX serves FTP.
Every captured file is length/hash checked and every archive entry is read back.
This establishes archive integrity, not a tested full restore or a sector image.
The source tag is immutable; subsequent video work belongs after that tag.

## Known limits

The working miniport retains the inherited RGB framebuffer mode; there is no
NV2A drawing acceleration or Windows mode switching. It uses diagnostic/PnP
wrappers, while the earlier plain path failed on hardware. The framebuffer
reservation is 4 MiB. Audio, bulk network traffic, long mixed-use sessions,
international filename compatibility and electrical power-off require further
qualification. Ftdisk49/Srv2013 warnings remain recorded. FATX has a counted
42-byte component name limit and cannot be advertised as Unicode/NTFS.

Post-tag finding: this diagnostic miniport also requires a fresh one-shot
`winnt/system32/xwn-video-trace.bin` seed before each boot. A populated trace
causes the deliberate `E0580001(0D,4,C000003E,10)` stop before the desktop.
Physical GDI attempt002 exposed an omitted reseed in a new test harness;
preserved trace bytes confirm that cause. Existing launch harnesses handle this
by preserving the old4096-byte trace and verifying a clean seed. The manual
dashboard menu itself does not perform that maintenance. Removing this diagnostic
dependency is necessary for unattended repeated menu launches; do not treat
the installed menu entry as a complete repeat-boot solution yet. This note does
not alter the tagged artifacts or qualify a replacement driver.

UnleashX's root Windows entry points to `E:\Applications\XWNFBoot\default.xbe`.
It is a manual menu action, not automatic Windows startup. The menu report
records the exact config path, before/after hashes and recovery copies.

Post-release update: [candidate0093](../video-trace-reuse-settled/README.md) now
passes two physical boots without a trace reset between boots and is installed
on the console. It reuses a valid existing trace file; it does not eliminate file
I/O or missing-file guards. The preceding one-shot limitation still describes
the immutable tagged driver/archive. The new overlay and rollback are preserved
separately; no change to0.1.0 artifacts or tag was made.
