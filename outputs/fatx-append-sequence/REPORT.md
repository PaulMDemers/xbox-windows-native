# Repeated append results — 7 October 2026

Both fresh sibling runs passed. Each completed 8,192 synchronous appends across
16 files, with 7,988,608 exact cold payload bytes. Total: 16,384 appends and 32
verified files. Per-append and end-only explicit flush, with retained and reopened
handles, all produced identical bytes for each starting offset. Neither run
reproduced the original physical setup-log anomaly.

Case001 completed its workload in18,645ms; case002 in25,515ms. These are incidental
timings, not a performance comparison. Both show normal shutdown/dashboard return,
five parseable hives, no unexpected errors/popups/application events, and full F
allocation consistency:323 directories,6768 files,324 directory clusters, zero
orphans/errors. Historical identical HID service failures remain classified in
the reports. SetupAPI stayed byte-identical at144,784 bytes in both settled boots.
The driver, video binaries and reviewed helper identities remained exact.

These are bounded serial, cached writes with an explicit final flush and normal
shutdown. Reopening can cause cache activity; end-only means no explicit flush
between appends, not absence of background disk writes. No diagnostic file I/O
occurs inside the append loop. Source bytes/counts and independent cold expected
bytes are separate checks. There was no debugger, host recorder or physical access.

Read-only inventory additionally located an actual pre-GPU-install fixture with
ConfigFlags1024 and no Driver class binding. Video/INF match the settled state,
but its older FATX0098 must be replaced explicitly before comparing0101. The
next first-install diagnostic is in ../fatx-first-install-0101 and uses the exact
previously tested targeted setup-completion helper. That UI-assisted run remains
a different evidence class from these ordinary append tests.
