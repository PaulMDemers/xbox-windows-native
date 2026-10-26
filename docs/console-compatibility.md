# Console compatibility and the incoming 1.6

The working Windows package is qualified on the original development Xbox.
Other console revisions remain unqualified. The next milestone is to expand that
coverage before native GPU acceleration. The user has now prioritized preparing
an incoming 1.6. The physical RCT process-cost comparison remains outstanding;
the [PC caller measurement](../outputs/rct628/REPORT.md) does not establish Xbox performance.

Networking/timer tests are tabled. [680](../outputs/revision680/REPORT.md) provides
a compiled, watched kernel-assisted 480p baseline tool for when the 1.6 arrives.
[681](../outputs/xcal681/REPORT.md) contains the Xcalibur source review and tested
host prototype. Neither qualifies Windows on 1.6; no native Xcalibur profile is
installed or ready for a Windows launch. See [current status](current-status.md).

## First additional-console inventory

A [user-supplied 1.6 report](../outputs/inventory630/REPORT.md) passes the schema-2
validator. It reports64MiB, kernel1.0.5838.1, about4.05GiB free onE, and an
unidentified encoder after both supported probes fail. Its current mode list
contains only640x480 and720x480 at32-bit/60Hz; it does not encode interlace flags.
Cable/adapter and dashboard HD-setting context is pending. This establishes a
useful inventory target, not Windows support or an intrinsic720p limitation.

## What the current source actually accepts

| Hardware observation | Current evidence and limitation | First useful next step |
| --- | --- | --- |
| Development console, 64 MiB, Conexant response | Working 720p Windows baseline, windowed RCT and user-confirmed saves/input | Retain as the comparison and recovery baseline |
| Another 64 MiB console with a Conexant response | Fits the explicit timing profile's encoder/RAM assumptions; boot, storage and input on that unit remain untested | Schema-2 inventory, package readback, then a watched initial boot |
| Focus response | Legacy video branches exist, but the reviewed explicit 720p adapter rejects this encoder | Review a separate Focus timing/handoff profile before a Windows launch |
| Xcalibur identified independently, or unidentified encoder | Legacy branches exist; the inventory intentionally does not infer Xcalibur from failed probes | Establish encoder identity and review its own mode/format/handoff path |
| 128 MiB upgrade or other RAM layout | The reviewed HD reservation explicitly requires 64 MiB | Design and validate a matching memory reservation across Xromwell, FreeLoader and the HAL; do not bypass the checks |
| SD cable, disabled HD mode, or unsupported display path | Not covered by the delivered E/720p profile | Select and qualify a separate matched mode/boot package |

These rows describe observed components, not a motherboard-revision decoder.
Record a known motherboard revision separately with its provenance. A revision
label, an advertised dashboard mode, or a successful inventory alone does not
qualify Windows support.

The relevant source constraints are concrete:

- [The explicit timing adapter](../src/boot/xromwell/drivers/video/xwn_hd_adapter.c)
  accepts 720p or 480p, encoder value 0, cable value 3, the matching enable flag, and
  the exact reviewed layout. It rejects other requests before its hardware writes.
- [The layout validator](../src/boot/xromwell/drivers/video/xwn_hd_profile.c)
  requires 64 MiB total RAM, framebuffer start at 55 MiB, a 9 MiB reservation,
  and 316,160 hidden bytes. These constants are a contract, not an autodetected
  universal allocation scheme.
- [Xromwell's Windows handoff](../src/boot/xromwell/boot/LoadReactOS.c) refuses
  non-64-MiB consoles when HD reservation is enabled. [FreeLoader](../src/boot/loader/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c)
  independently requires 64 MiB and the exact two-entry memory map in that build.
- [The native timing wrapper](../src/boot/xromwell/drivers/video/xwn_hd_native.c)
  resets or halts after a partially applied display setup. An unsupported request
  returns to the legacy setup path only for the default 720p selection; explicit
  480p refuses it. That fallback is not a qualified alternative Windows HD profile.
- [Legacy encoder detection](../src/boot/xromwell/drivers/video/BootVgaInitialization.c)
  labels the encoder Xcalibur if both earlier probes fail. The newer
  [inventory tool](../src/utilities/hardware-report/main.c) and
  [host validator](../tools/hardware_report.py) deliberately retain
  `unidentified` instead. Review this discrepancy before using unknown hardware;
  do not turn an I2C failure into a support claim.

No maintained loader or driver change accompanies this review. The separate681
prototype corrects four-byte read handling and bounds modeled encoder transfers;
it has no native I/O/timer binding yet. Legacy Xcalibur HDTV code always chooses
its 480p table, regardless of the requested mode. Existing branches are useful
starting points, not proof the shipped profile works with those encoders.

## Qualification sequence

1. Collect the existing schema-2 hardware report from each available unit using
   the [tester instructions](testers.md). Record kernel version, RAM observation,
   encoder response, GPU/MCP revision, AV pack, dashboard modes and E free space.
   Keep personally identifying data, EEPROMs and firmware out of public reports.
2. Group the reports by actual encoder/RAM/boot differences. For the incoming1.6,
   start with the watched680 kernel baseline, then qualify a separate native
   Xcalibur480p pattern before Windows. Treat RAM upgrades as a separate task.
3. For a new profile, review timing, color format, stride, framebuffer extent,
   hidden/reserved memory and handoff consistency as one change. Validate pure
   calculations and rejected configurations before a watched hardware launch.
   Never borrow another console's firmware state or remove validation gates.
4. Use unique E paths and exact source/binary/readback pins. Keep dashboard C,
   ordinary startup and the development console's 720p package intact. Preserve
   the existing package as recovery; do not merge installations.
5. Record initial boot, desktop geometry/colors, mouse/keyboard, a small file and
   image save/reopen, normal restart and subsequent save readback. Preserve failed
   boots and distinguish a reset from a normal Windows shutdown. Audit relevant
   files, hives and events before closing an attempt.
6. Publish a per-unit result tied to the exact report and package. Expand the
   supported matrix only after those observations. Test RCT later on newly
   qualified units; it remains excluded from the distributable Windows kit.

Boot intermittency and the separate 1080i investigation remain documented issues.
A cold-start workaround is useful operationally but does not establish a boot fix.
Sound remains deferred for the RCT milestone. Native acceleration follows the
compatibility work, with a separate offscreen GPU proof and graphics sample ladder.
