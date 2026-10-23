# 668 CLOSED: host-only interrupt contract audit

Read REPORT and audit001.10 static checks,12 handler cases and5 sender-entry
cases passed against pinned667 source/binary artifacts. No console connection,
new XBE, runtime reopening, driver patch, receiver or hardware change.

IF-set NativeSend656 returns before PCI/NIC work. nInteruptable==0 does not
suppress timer/VSync/SMC effects; it cannot replace the IF-clear gate. The helper
intel_interrupts_on changes APIC-base MSR only, not IF; preserve that correction.
Existing allocator normal paths enable IF, consistent with physical667's
memory-detection boundary observation. No Windows/480p cause is established.

Next create a fresh HOST-ONLY terminal transport design/candidate after frozen
capture. Keep original capture and pre-transport CPU state distinct from any
deliberate post-capture exclusion. Specify entry/reentry rejection, immutable
bytes, cleanup failures, held-state policy and exact state preservation rules.
Keep native admission checks; later gates are still unqualified. Independently
validate before a new binary/build/console launch. No speculative global
allocator fix, firmware-state borrowing, pending-bit clearing or gate waiver.
Do not silently apply CLI or relabel modified state as original capture.

Original Xbox last confirmed dashboard; ordinary720p/startup/XBOX480/releases
protected. No hook/owned host process. Physical lease retained; build lease
free; persistent firewall retained; automation paused. No user action needed.
