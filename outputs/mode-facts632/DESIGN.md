#632 read-only missing mode-fact probe

The physical631 stock-API transition passed, but the private4034 kernel capture
used by310 is no longer located. This fresh probe reads selected programming
facts from the current original development kernel. It does not dump firmware,
read display/encoder state, write display registers, or enter Windows.

Before table access: require1.0.4034.1 and exact AvSetDisplayMode address; validate
all touched page segments; validate PE signature/machine/magic/timestamp/size;
SHA256 the entire1181-byte setter against the retained307 digest. Require exact
table-index lists and both known720p/1080i programmed profiles. Only then extract
mode0x88080801 and apply independently reviewed32bit pitch overrides. Header and
setter scratch are not exported. Output contains only selected register facts.
This is source-derived programming data, not firmware-state replay.

Range checks reject zero/oversize/out-of-image/overflowed reads before copying.
No allocation, interrupt-state change or MMIO/SMBus access in the probe. Kernel
API calls still have no hard execution deadline. Private memory stays private.
Log uses CREATE_NEW, bounded records, flush per line and explicit close status
in the debugger receipt. COMPLETE is before close; durable physical readback
and dashboard return are independently required. No startup hook is needed.

Host001 uses synthetic memory. Real SHA passes9 independent hashlib vectors;
wrong kernel is rejected without a memory read; synthetic setter is rejected.
A separately compiled DIGEST_MODEL tests deeper branches and is never compiled
into the XBE. It supplies no actual4034/480p facts. Emulator must exercise native
refusal on4627 without a read. A later isolated physical collection is needed.

The fresh emulator uses the unused official blank8GiB and private EEPROM, never
an executed runtime parent. Input copies are below32MiB;128MiB projected C space
allows96MiB for logs/overlay.20GiB reserve remains. Preserve disk equality failure
if the historical reserved-sector byte changes; do not promote the image.
