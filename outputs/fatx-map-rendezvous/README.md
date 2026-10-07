# Bounded dirty-mapping / volume-flush overlap

This NEW kit follows the failed coverage attempt in ../fatx-map-truncate.
Its failures remain unchanged. No FATX/video driver or inherited emulator
configuration changes. The parent is settled0101/video0093 with the same
synthetic null-device and unsupported-device policy, not physical support.

Both modes use the same source/binary and independent byte/allocation oracle:
11 files,4 rounds,18 appends each =792 cycles,32 queried allocation-size
decreases,132 immediate reopens,11 final cold files. The35-byte mapping allowance
crosses65536/131072 for selected prefixes while finalEOF releases that cluster;
later appends regrow it. AllocationSize is queried, not an intermediate raw FAT
snapshot. Only final allocation receives the complete independent cold scan.

For the first append of every file-round, concurrent mode publishes a unique
dirty epoch AFTER writing the mapped payload, then waits at most10 seconds for
an event. The worker signals only after a complete successful volume
FlushFileBuffers call whose before/after dirty-epoch values are identical and
nonzero. Main clears the epoch before seek/unmap/EOF shrink. All44 file-rounds
must have both positive append overlap and positive dirty-map overlap. Total
rendezvous count must equal44. No coverage requirement is removed.

Serial mode has no worker and holds its first dirty mapping for100ms. This is
a functional serial control, not identical scheduling or a performance control.
Remaining17 appends use2ms dirty dwell in both modes; the concurrent worker
continues freely through unmap/shrink/regrowth. The rendezvous proves temporal
containment of a volume API call inside dirty mapped residency, not simultaneous
kernel instruction execution, a specific cache write, or a power-loss guarantee.

Every reported failure signals worker stop and attempts a bounded60-second
join; ABORT_JOIN records the result. Failed/hung I/O can still require the owned
host deadline. A join timeout is retained as failure, never normal shutdown.
Successful runs require completed worker join, full workload, pending-install
idle, explicit normal restart, actual dashboard return and cold audits.

check-oracle.py rejects11 incomplete/invalid protocols, including absent dirty
overlap, short rendezvous count and aborted worker. Static imports and dynamic
NT5 exports are checked against owned DLLs; compiler/source/binary/fixture pins
precede launch. Preflight snapshots all pinned source bytes per case. Serial
workload/integrity must pass before the concurrent diagnostic comparison.
Strict SCM/Ftdisk errors remain failures in either case; no recovery promotion.

Emulator-only. Never access the physical console. Each fresh attempt launches
once and collects once. Preserve original failed coverage run, physical0101/
video0093,0088rollback,immutable0.1.0 and all earlier interruption evidence.
