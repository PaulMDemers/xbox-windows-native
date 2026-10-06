# Shutdown and capacity diagnostics

FATX0098's third physical soak completed its full workload and cold integrity
checks, but its shutdown popup and Srv warnings remain strict failures. This
investigation observes the existing stack; it does not suppress errors, set
FAILEDINSTALL flags, install a replacement driver, or delete partition contents.

## Physical evidence from the completed soak

`physical-inventory.json` reads the captured, hash-verified SYSTEM hive and
SetupAPI log. Latest boot shows the client installer for PCI10DE:01B0, described
as Multimedia Audio Controller, with no Driver or Service registration and a
no-compatible-driver result. This is a concrete pending-installation lead, not
proof that the process generated the later popup.

The captured drive mapping, cross-checked with the pinned Xbox HAL partition
table, is:

| Windows | Dashboard | Start byte offset |
| --- | --- | ---: |
| C: | F: | 8004132864 |
| D: | E: | 2884108288 |
| E: | Z: | 1573388288 |
| F: | C: | 2359820288 |
| G: | X: | 524288 |
| H: | Y: | 786956288 |

Srv's EventMessageFile resolves to the owned NT5 netevent.dll. Its exact
0x800007dd message says the disk is at or near capacity; `srv-message.json` pins
the source hash and language. The warned F:/G:/H: therefore refer to system C:
and cache X:/Y:, not the large dashboard F: containing Windows. This alone does
not establish actual physical free space, a free-space accounting bug, or a
relationship to the dashboard's shadow C. No threshold was changed.

## Diagnostic helper and emulator

Original `probe.c` exclusively creates C:\xwnsd01\probe.log. Five samples over
120 seconds record drive device targets, both free-space APIs, selected process
IDs and bounded read-only command-line reads, plus visible window titles. It
then requests normal restart. No registry/device-state writes, automatic dialog
dismissal, force-termination, driver replacement, or debugger intervention.

Pinned RosBE compilation, owned NT5 static/dynamic export checks and binary hash
are in probe-review.json and dynamic-import-review.json. The fresh owned001
child preserves all registry hives and installed drivers during preparation.
Its exact backing/seed and private emulator identities are retained.

Emulator001 completed all samples and a normal restart, with unchanged payloads,
five traversable hives, no new popup or unexpected error. It observed the GPU's
newdev installer at all five samples and a visible hardware wizard. Thus an open
installer by itself is insufficient to predict a shutdown popup. This single
passing diagnostic is not a fix for the intermittent failure. Its free-space
APIs agree, but its partition contents differ from physical hardware.

The user-authorized physical diagnostic uses the exact emulator-validated helper,
with a single recorded launch and normal-startup restoration before collection.
Results belong in physical-observations.json and physical-audit.json; do not
infer them from emulator001. All previous soak failures remain unchanged.

## Physical diagnostic result

Single launch15:35:02UTC, dashboard observed15:38:03UTC, normal startup restored
before collection. All five samples completed (last120345ms), normal shutdown,
unchanged baseline/helper hashes and no new popup or unexpected error. This is
a bounded diagnostic PASS, not the15-minute workload's qualification result.

At the final sample Windows reported:

| Windows / dashboard | Free bytes | Percent free |
| --- | ---: | ---: |
| C: / F: |100302127104 |41.440% |
| F: / C: |2932736 |0.559% |
| G: / X: |22740992 |2.892% |
| H: / Y: |48562176 |6.176% |

GetDiskFreeSpace and GetDiskFreeSpaceEx agree. These are two queries through the
same filesystem, not an independent raw FAT count. The low reported capacities
account for the previous warning condition on the three small partitions; do
not infer corruption of the large boot/data partition from their drive letters.
The shorter run's lack of warning events does not resolve a periodic capacity
warning. No files were removed or quotas/alert thresholds changed.

The audio01B0 newdev command and visible hardware wizard were still present at
the final sample, yet shutdown was clean. Paired with the emulator's pending GPU
wizard and clean shutdown, this rules out the simple inference that an open
wizard always produces the popup. It does not rule out an installer-queue race.
Captured pre/post SetupAPI bytes have an exact preserved prefix and new records
show no compatible driver for01B0. There was no new installation-state edit.

Next causal experiment: observe the installer process creation/exit sequence
across shutdown, including whether closing the active wizard advances the queue
after shutdown has begun. Identify the specific process raising the hard error
in a failing run before changing queue/device policy. Existing resolved-target
debugger scripts are diagnostic aids; an ordinary passing control must remain
in the record. Do not mark unsupported hardware installed or disable devices
as a purported FATX fix. Video optimization remains a separate workstream.
