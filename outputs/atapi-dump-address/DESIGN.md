# ATAPI dump-address diagnostic

The user renewed authorization with “Proceed” after the October 7 cutoff.
This is a new emulator-only session; the old automation remains paused.

Crash005 is a fresh sacrificial child of the same immutable parent used by
crash004. It uses unchanged FATX0103, HAL0102, video0093, NVNet0104, dump settings,
and inherited emulator null-device/unsupported-device policy. Physical0101,
video0093, original0088 rollback and immutable0.1.0 are untouched.

Static inspection of the pinned actual atapi.sys shows that dump writer
RVA13454 performs a 64-bit partition/volume addition, divides by sector size,
and calls RVA27fe directly. That routine masks the high LBA byte with 0x0f at
RVA28e7 and emits only three other address bytes. The actual cold registry
already has EnableBigLba=1. No setting or driver is changed to force success.

New one-shot breakpoints capture the first write's dividend/divisor, quotient,
constructed SRB/CDB, decoded LBA, high byte before/after the mask, selected
command and actual port-call arguments. Every site must match the pinned PE
after relocation. Capture is bounded and paired with the first writer's thread
and stack; all breakpoints are removed before capture and owned cleanup.
The unchanged lower writer is expected to reproduce the bad address. The
diagnostic succeeds only as localization evidence, never dump qualification.

Complete the existing cold allocation, hive, protected binary, configuration,
pagefile map and alias audits. Preserve the crash disk without recovery boot.
No file-content safety claim follows from metadata or selected hashes alone.
Never relaunch or recollect closed crash001–004, or reuse crash005 after launch.
