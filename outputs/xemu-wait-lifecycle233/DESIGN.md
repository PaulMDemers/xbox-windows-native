#233 isolated compiled read-only wait observer

Observer enabled only by selecting this fresh diagnostic executable. Resident
256-row overwrite ring, monotonically saturated64-bit sequence, protected by
existing PGRAPH lock. Nonzero NO_OPERATION before/after and IRQ-update-return;
guest INTR acknowledgement before/after, enable writes and reset before/after.
No new lock acquisition in record calls. FIFO data valid ONLY where the caller
already holds FIFO AND PGRAPH locks; producer samples mark it unavailable.
QOM getter try-locks FIFO then PGRAPH without blocking BQL; takes no mutable
emulated action, allocates no record storage and never clears waits/interrupts.
Fixed two live samples250ms apart then separate stopped-dashboard request.
No empty-state search/retry or resumed producer within preservation request.
232 parser/publication/GL code otherwise unchanged; no guest/native GPU grant.
Bounded ring overwrites explicit, missing pair boundaries kept as unknown.
One first-boot/restart cold audit, not repeated-boot storage qualification.
