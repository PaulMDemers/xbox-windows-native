# Ordinary ATAPI0105 comparison

Both fresh control001 and candidate001 are closed and strict PASS. Each completed
792 appends,32 allocation shrinks,132 reopens and11 exact cold files. Two bounded
TCP exchanges each transferred32x4096 bytes in both directions. Both returned to
the dashboard after one normal shutdown, with clean complete allocation,
five structural hives, protected hashes and no warning/error/application deltas.

The pair manifest proves only atapi.sys differs. FATX0103,HAL0102,NVNet0104,
video0093,HidServ,96MiB pagefile and crash-dump settings remain identical.
The inherited emulator synthetic null/unsupported-device policy is unchanged.
The inherited audit limits sentence mentions the earlier NVNet comparison; the
actual protected-file comparison in pair-review.json establishes this ATAPI pair.
A verifier initially invoked on Windows failed to import the WSL-only FATX tool;
the correct WSL invocation passed. Neither guest was repeated.

See pair-review.json and each case's audit, network-verification, evidence and
closure records. This ordinary comparison does not alone qualify a crash dump,
recovery or physical hardware. No physical access occurred.
