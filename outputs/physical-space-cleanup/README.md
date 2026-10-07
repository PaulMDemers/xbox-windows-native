# Authorized physical cache cleanup

Completed 7 October 2026, 01:39 UTC. Six enumerated game-cache map files were
removed from dashboard X and Y, reclaiming 1,488,977,920 file bytes (1.39 GiB).
Each was first archived to the private E: host artifact directory, SHA256 checked
against a local reread, then read and hashed again from the console immediately
before deletion. The backup and removal manifests preserve exact names, sizes,
hashes and timestamps. The journal prevents accidentally repeating deletion.

Only cache002–005.map on X and cache000–001.map on Y were deleted. Final listings
match their original listings minus exactly those six files. Savegame files,
preferences, fonts, directories and every C/E/F file remain untouched. Games may
regenerate their caches. No claim is made yet about the next Windows event log.

Dashboard C exposes eleven files totaling 3,259,668 bytes, principally the
UnleashX executable and its assets. That does not explain the earlier Windows
raw-system-partition free-space reading. No dashboard or softmod file was deleted;
the separate raw-C inventory investigates this discrepancy read-only.

Private cache payloads reside at
`E:/Codex-private-artifacts/xbox-windows-feasibility/cache-cleanup-20261007`.
They are not repository or release contents. Windows startup, FATX0101,
video0093, rollback payloads and immutable 0.1.0 were not changed by this cleanup.
