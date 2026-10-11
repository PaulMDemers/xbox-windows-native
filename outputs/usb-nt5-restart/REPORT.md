# NT5 XID restart and subsequent-boot results

The installation run passed 200 HID reads and a normal restart after three exact
known hardware wizards were canceled. The subsequent boot failed: its new log
files contain stale disk bytes, and the filesystem has a broken chain and one
orphan cluster. This does not qualify repeat-boot persistence or physical use.
Both guest instances are closed. The physical Xbox and shared baseline are unchanged.

## Installation and restart: emu001

The driver logic is unchanged from commit 893a239; copying normalized its line
endings, which the initial byte comparison detected and recorded. Build001 and
actual NT5 import review passed. The 78,915 HID mapping checks and nine isolated
USB transport fault schedules passed. The pinned wizard006 helper was staged
under the private xwnxid path; the fixture's original wizard binary was untouched.

One Windows launch was accepted at 2026-10-10 20:28:38 UTC. Two open/read/close
cycles completed 100 HID reads each. The helper canceled exactly targets 1, 2
and 5: the recognized APU, audio and emulator PCI instances. Each action matched
its exact process command, active welcome page and enabled Cancel control;
closure and process identity were logged. These devices were not installed.

The helper completed after 9,495 guest milliseconds, including 5,115 ms
of genuine install-queue idle. The probe joined it with exit 0 and observed another 5,100 ms
of idle, checked the queue again, and requested one normal unforced restart.
The dashboard returned at 20:30:38 UTC, with exactly one new EventLog 6006 record.
No debugger pause, screenshot pause or manual controller input was used.

Cold inspection passed all protected/staged/installed-file checks, full allocation
ownership, five hive traversals, historical log preservation and selected typed
policy checks. There were no new device-disable flags. Natural binding changes
are retained in emu001/device-state.json. Strict event checks remain false due
to DCOM 10005 and Ftdisk 49; their causes are not attributed to the XID driver.

The generic collector flagged the missing exit.txt shell marker and therefore
reported input_smoke_pass=false. That echo runs only after the probe process
exits and is not a reliable required record after a reboot request. The original
collector result and initial failed review remain intact. The independent
restart-review.json uses the durable probe/helper records, shutdown event,
dashboard return and cold checks, while explicitly retaining the missing marker.
This is a scoped restart pass, not a blanket system pass.

## Subsequent boot: emu002 — failed

A fresh child disk was created from closed emu001. The installed driver was
retained byte for byte. A separately compiled verify-only probe performed no
installation and launched no wizard helper. Before boot, parent bytes, protected
files, staged files and full allocation were checked. All prelaunch checks passed.
One launch was accepted at 20:33:41 UTC. The dashboard did not return within
300 seconds; the owned process was host-stopped. There is no new shutdown event.

The cold verification log cannot be parsed as text, so no HID-read result or
probe exit code can be claimed. Independent qemu-nbd and qemu-img range readers
agree on file bytes, directory entries and the complete FAT:

- verify.log is 2,226 bytes in cluster 2682. Every byte equals the preboot data
  in that previously free cluster; its new FAT entry is end-of-chain.
- exit-verify.txt is four bytes in cluster 2144564, also exactly the preboot
  stale data in that previously free cluster.
- CIM.REC still declares 705,881 bytes starting at cluster 2144533, but that
  FAT entry changed from 2144534 to zero, producing an invalid and short chain.
- Cluster 2144563 is newly allocated but orphaned.

The parent disk remains exactly SHA-256
ba5ed2d755e90bf3a9a599fd3ee106526841f4325e94db3f03aa91eb1ef2b890.
The installed driver and all protected/staged files remain exact in the failed
child, and the five hives still parse. Those facts do not override the payload
and allocation failure. No new decoded event errors were found, but no new
shutdown event was found either; an empty event delta is not a successful boot.

See emu002/forensics.json, emu002/verify-review.json and the before/after allocation
records. Raw non-text payloads and the original full collector output are kept
privately with hashes; they are not distributed as successful text logs.
The cause is unresolved. A host-stopped run cannot establish normal-shutdown
durability, and stale data alone does not identify which guest writer failed.

## Next work and limits

The immediate priority is the repeat-boot storage failure: retain both disks,
reproduce in a fresh controlled child, and trace file data versus allocation
updates before further controller changes or hardware trials. Never relaunch,
repair or rebase these closed evidence disks in place.

The controller still vetoes query-stop/remove while started. Proper PnP state
restoration, cancellation, stop/removal and device-power trials remain pending.
[Microsoft's query-remove guidance](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-an-irp-mn-query-remove-device-request)
requires preserving the previous device state for canceled removal requests.
No deliberate controller-input mapping or physical driver deployment is qualified.

## Reconstruction

Source parent: 893a239f4a374d698d4134b4f1f7ea1b7bf4fccf.
Build001 driver: c370b7f185beef757b971dea01de8c3df30ee968aa22f804da5d52fa337b2680.
Build001 probe: 5681c18e48a4fd9f2fc1287f1cbfea644a70adf0335db1d97794857c8efd5a52.
Verify001 probe: 8003fceb1a03797531a8898356266cea0c3ed8cf6a595b68493fa936184e456a.
Wizard006 helper: b3a42114e2d083d3d124cb54199a8d6c3fd63fee5a9ef6b196e4599d28b84fbb.

Build commands, linked imports, prelaunch source hashes, exact per-case source
snapshots, stage/launch/cleanup records and independent cold reviews are retained.
The manifest freezes the source and evidence; runtime claims are per case.
