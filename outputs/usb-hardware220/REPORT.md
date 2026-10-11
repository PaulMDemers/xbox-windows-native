# USB220 physical descriptor result

The single Windows descriptor trial completed its log. The physical child is FFFF:FFFF, revision 0100, with XID interface 58/42/00. It remains unbound and unconfigured; no controller input reports or functional gamepad support were established. No driver, INF, HAL, video, SMBus or AC97 change was deployed.

## Actual physical evidence

Windows launch was accepted once at 2026-10-10T06:07:51.539346+00:00. The user later reported exactly "the xbox was restarted"; the restart method and prior screen state were not specified. On verified owned-dashboard return, normal startup was restored FIRST at 2026-10-10T15:37:12 UTC, then results were captured. No Windows relaunch occurred.

Collector build007 completed 20 requests in 25,575 ms, with one failed driver-key query (request 19, error 2) for the unbound XID child. Parsing found no structural issues. The complete end marker supports descriptor-workload completion. The separate exit.txt is zero bytes, so a process exit code is unavailable. The startup line places %errorlevel% immediately before >; a numeric expansion can be consumed as a redirection descriptor. Preserve this original harness and result; separate the value from redirection in a future trial before relying on that sidecar. Do not infer a zero process exit status.

The live topology contains a 0451:2046 hub, revision 0125, at root-hub port 1, and the FFFF:FFFF child at that hub's port 3. Its configuration descriptor specifies interrupt IN 0x81 and OUT 0x02, each 32 bytes with interval 4. The device reports configuration 0 and zero open pipes. These physical addresses differ from the emulator's IN 0x82 and must not be substituted with emulator values. No live mouse or keyboard was reported in this capture. The keyboard remained unplugged. USB service/Enum typed values are identical before and after the trial.

The collector uses standard hub queries. Vendor XID descriptors and interrupt input reports still require a separately reviewed transport; descriptor capture does not install or validate a gamepad driver or identify an exact controller model.

## Integrity, events and restoration

All five primary hives passed before/after format, checksum and sequence checks. SYSTEM has no added/removed keys and 23 changed values; USB service/Enum metadata is unchanged. Selected protected files, the collector, startup backup and full rollback ZIP matched their recorded hashes on post-run readback.

The full F allocation scans before and after the Windows trial passed with zero errors and orphan clusters. Before: 6193 directories, 122554 files, 6198 directory clusters. After: 6194 directories, 122559 files, 6199 directory clusters, including the new trial directory and its five files. These are allocation checks, not a hash audit of every file's contents.

The existing event history was preserved. Five new system events include Ftdisk 49 (error, record 323) and Srv 2013 (warning, record 327, F:). Strict event qualification therefore FAILS. There is no new EventLog 6006 record, so normal shutdown durability is unqualified. SetupAPI retains its prior prefix and adds 1822 bytes, including no-compatible-driver 0xe0000228 and an explicit pending PCI 10DE:01B0 install attempt. No event or failed installation was suppressed.

At 2026-10-10T15:40:51.249261+00:00 the exact incoming startup, five primary hives, 13 registry journal/backup companions and all protected files were restored and readback-verified at the dashboard. Event history and diagnostic outputs remain preserved. The final restored allocation scan also passed: 6194 directories, 122559 files, 6199 directory clusters, zero errors and zero orphan clusters. Final owned-dashboard readback at 2026-10-10T15:43:16.184485+00:00 matched all 50 baseline files (32 protected/startup files, five primary hives, 13 companions), with unchanged registry-directory inventory. USB released its queue ticket at 2026-10-10T15:43:32.962051+00:00. PCI may claim the console. No further USB physical access is scheduled.

## Evidence and continuation

Source/evidence root:
E:/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/usb/repo/outputs/usb-hardware220

Use physical001.json, observation001.json, audit001.json, before/after-hive-audit.json, the three phase-specific scan/allocation records and user-observation-request.json. audit001.json was produced before the final restored scan; its allocation list contains before/after only. The final restoration result is recorded in completion.json. HELD.json preserves the earlier bounded-observer hold. Raw logs, hives, full metadata and rollback bytes remain private under artifacts/physical001. Remote recovery files remain at /F/xwnusb220a. Frozen inputs are in prepared.json; previous revisions and earlier failures are retained. The unchanged collector SHA256 is b79d517414d588947432705d9089348ac66711a3a4de44497139293552d9e5b1.

Next engineering work: reviewed vendor-XID and input-report access for the actual FFFF:FFFF device, followed by a bounded driver design and separate qualification. This descriptor-only trial provides no repeated-boot or clean-event PASS.
