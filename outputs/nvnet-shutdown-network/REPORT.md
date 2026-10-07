# Matched NVNet ordinary runs both pass

The new control001 and candidate001 each completed792 mapped appends,
32 queried allocation-size decreases,132 reopens and11 exact cold final files.
Each verified two real TCP exchanges through the emulated NIC:32 requests of
4096 bytes each, before and after the workload, totaling262144 bytes in each
direction. Independent host transcript hashes match the deterministic requests
and transformed responses. Both returned normally to the dashboard and recorded
one EventLog6006 shutdown.

Both strict results are TRUE. Each full cold allocation audit found323
directories,6765 files and324 directory clusters, with no errors or orphans.
Five hives parsed; all protected binaries, helper payloads and startup bytes
matched. Neither run added warning/error or application events. No debugger,
dialog cancellation or guest UI intervention was used.

Only the NVNet binary differs between the pair. FATX0103, HAL0102, video0093,
restored HidServ, initial hives, helper, parent chain and inherited emulator-only
null/unsupported-device policy match. CrashDumpEnabled remains3, with the same
96MiB/1536-cluster pagefile and first65536 bytes mapping to volume offset
140436013056. The new host connection uses an explicit loopback-only forward;
restrict=on remains enabled. See pair-review.json and verify-network.py.

Control launched12:00:13UTC; candidate launched12:04:42UTC on October7,2026.
Both are CLOSED. Never relaunch/recollect either. The earlier incompatible
outbound TCP harness is preserved separately in ../nvnet-shutdown-resident;
its failed result is not superseded by a PASS marker in that directory.

These ordinary runs establish bounded normal-network/storage/shutdown behavior,
not crash-dump completion or physical qualification. The next separate
../nvnet-controlled-dump/crash003 uses the unchanged one-shot crash trigger and
pins actual shutdown/dump execution. All physical baselines remain untouched.
