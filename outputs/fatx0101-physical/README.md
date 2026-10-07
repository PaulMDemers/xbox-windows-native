# Candidate0101 physical concurrency trial

One authorized physical launch at 2026-10-07 00:50:29 UTC. The preflight verified
the recorded FATX0098/video0093 baseline and normal startup. Latest human Proceed
was accepted as readiness after the keyboard-unplug request. Xromwell's Razer
keyboard hang remains a constraint for future launches.

The exact emulator-qualified driver is
`ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9`, from tree
`8e12297ca0ed53383fe9aaebef152c26aee5a43b`. The unchanged five-worker helper is
`aca62d7200e9fb1936ea9c33a1538b96ad8bbeebfb2970b6bff4a689408b5a6d`.
Eligibility pins two independent emulator stress passes and a full fifteen-minute
emulator mapping/BMP soak. Those remain emulator evidence only.

## Ownership and rollback

Staging is dashboard `/F/xwn101a`, distinct from the helper's exclusively created
`/F/xwncc01` output (Windows `C:\xwncc01`). Original driver and normal startup are
preserved both privately and in the staging directory. Every uploaded payload is
read back before launch. Video0093, loader/HAL, original0088 rollback, prior test
folders and immutable0.1.0 are unchanged. No PnP policy or INF is transplanted.

`physical.json` records launch intent before SITE EXEC; never repeat it even if
the reply is uncertain. `watch.py windows` observes that single launch only.
The helper waits up to ten minutes for its five workers, then holds on timeout.
It also holds when device installation is pending; it never forces a restart.
The observer stops after thirteen minutes; dashboard absence alone is not a
crash diagnosis. Ask for the screen once if that is the remaining evidence.

On return, `physical.py collect` restores normal startup FIRST, then captures
logs, outputs, events, SetupAPI, trace and payload/rollback hashes. Collection can
resume an interrupted capture only when already preserved bytes still match;
completed collection is guarded. `physical.py rollback` restores0098 and startup
without launching, after evidence preservation when rollback is appropriate.

## Gates

Five workers must each complete500 rounds with zero errors: two4097-byte file
writers, one volume flusher, one truncate/extend/rename/attribute worker, and one
directory enumerator. The three final files must match the exact last-round
patterns; `meta.tmp` must be absent. Require normal restart request, one orderly
EventLog start/stop pair and observed dashboard return.

Strict event comparison retains the existing exact-signature historical
SCM7000/Ftdisk49 exceptions only. New Srv2013 warnings, popups and application
events fail. Previous strict physical failures are not erased by this attempt.

After provisional qualification, `scan.py launch` starts the existing owned
read-only allocation helper ONCE at `/E/Applications/XWNLock101a`. Observe and
collect its unique output, then run `audit-binaries.py` (resume only incomplete)
and `qualify.py` again. Full allocation,3439 hashes and nine structural hives
are required. No recovery bundle or release qualification follows a partial pass.

This test is not the15-minute hardware mapping soak, an actual Paint UI test,
generic PnP qualification, arbitrary mapped truncation testing or a video change.
Current state is in the JSON records and the main continuation note.

## Host observation at01:03UTC

The13-minute observer ended without dashboard return. Screen state and workload
outcome remain unknown; this is neither a pass nor an established deadlock.
One screen question is pending. Normal startup is still pending restoration
because FTP is offline. No collection, allocation scan, binary audit or recovery
capture has run. The host observer exited; no background process remains.

At01:05UTC the user supplied a photo of the Windows desktop with an open hardware
wizard, Getting Started and cmd. Device name is obscured. FTP refused connection.
The workload outcome is still unknown. Requested final probe.log lines; no wizard
was dismissed or test relaunched. The pending-install guard holds indefinitely,
so dismissing a wizard would not automatically resume this helper's restart.

At01:10UTC a second photo shows all five500-round workers completed in62205ms,
zero API errors, and RESTART_BLOCKED_PENDING_INSTALL258. This establishes the
reported guard reason; exact files and cold checks are still pending. The host
qualifier now describes worker completion separately from the strict restart
protocol gate; no gate was relaxed. Requested current hardware wizard device
identity before changing installation choices. No scan or new launch occurred.

## Completed cold result

Collected once after user-reported clean normal restart; normal startup restored
first. Exact log corroborates62205ms and all five500-round counters/errors.
Three final files match every byte; meta.tmp absent. One normal EventLog shutdown,
no new popup/application event. ThreeSrv2013 warnings for WindowsF/G/H recur.
Automatic-restart protocol and original observer gate remain FAIL; user-assisted
return is explicitly separate. Overall strict qualification remains FAIL.

The unique read-only scan returned and was collected once:6074 directories,
122320 files,6079 directory clusters, allocation consistent,0 orphan clusters,
0 errors. All3439 manifest binaries match and nine registry hives pass structural
checks. Final read-only console verification confirms0101/video0093, normal
startup and preserved0098 rollback. No new Windows run or recovery capture.
All owned observer/audit processes are closed.

SetupAPI is an exact extension of the prior saved log. It records the installer
queue for10DE:01B0,01B4,01C1,02A0 and USBffff:ffff without compatible drivers,
followed by successful Razer1532:021E and mouse/HID installations. The current
keyboard instance persists withkbdhid,keyboard.inf andConfigFlags0. PCI registry
state is unchanged from the earlier snapshot: GPU hasXboxVnt5 service, flags0x400
and no completed Driver binding. Other historical entries are not a live bus
inventory. This manual setup cycle does not prove an unattended popup fix.

Next: complete supported GPU PnP registration with the preserved driver package;
handle unsupported devices explicitly; independently investigate the small-volume
capacity warnings. Preserve this failing protocol record and use a new attempt
for any later unattended test. Ensure keyboard is unplugged before Xromwell.
