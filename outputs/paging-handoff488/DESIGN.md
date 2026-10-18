# Isolate the privileged sequence before another console launch

Use exact487 XBE851a916d... and483763b9516...; extract1024 bytes at the actual
blentry symbol70310 (file offset4774). Full extracted SHA256:
c039a983e17220bd6150e888e7a8c791134c03dbaca555d236158b41694ace2e.
Original far-pointer offset74, newloc80 and critical end224 are unchanged.
No Xbox code is compiled or patched for deployment. The fixture performs the
ordinary far-pointer relocation in its two in-memory copies. Fault variants
deliberately alter synthetic memory after that setup; they are never candidates.

The Multiboot ELF enters a synthetic flat protected-mode environment. Page tables
at01000000/01001000 identity-map64MiB except02000000, whose PTE points at000c1000.
Both physical pages hold the extracted code. A high mirror is also mapped; the
test does not assert the real Xbox's entire map. Source is01f00000, destination
02600000, original entry is02000000. A deliberately unmapped ESPd001cd7c exercises
the no-stack interval already identified in464. IF/DF are initially0x282;
external PIC interrupts are masked. Exception IDT is empty so fault cases terminate
with independently inspected exception/triple-fault evidence. No interrupt or
cache-race coverage is inferred.

Positive cases: dual-copy nonidentity and identity-mapped low entry. Fault cases:
absent PTE, UD2 at first instruction after PG disable in physical copy, UD2 at
low alias entry, zero far target with explicit UD2 there, corrupt payload entry,
DF set, wrong source. Short-copy variant reduces the actual copied count by one:
the entry oracle must execute and reject the complete1MiB comparison. Input DF
was clear in both actual console records; the DF case is a negative, not a new
physical hypothesis supported by observations.

Independent oracle checks architectural postconditions without using the old
stack. Debug bytes B/E/P mean fixture setup/owned payload entry/full check PASS;
F means oracle failure. Explicit debug-exit codes33/35 accompany these receipts.
No machine result is accepted solely from process exit0. Each case has a12-second
watchdog and bounded termination fallback; any deadline fails qualification.
No fallback was required. VM execution uses the existing exclusive emulator lease,
no networking, no virtual storage, no physical devices, no KVM. Each unique case
runs once; all prior failures and attempts are immutable.

Tool/input pins include the exact QEMU, BIOS, Multiboot loader, assembler/linker,
objcopy and resolved dynamic libraries. Before/after hashes are checked. Private
builds use C, with64MiB build and128MiB run reserve above20GiB; no E allocation.
The original run scripts/models and all outputs are retained for audit.

Intel SDM24.30.3 recommends identity mapping across paging changes and notes that
MOV CR0 is serializing for P6, so a near jump is not required on that family.
Do not promote the missing near jump alone as a defect or introduce a cosmetic
jump as a claimed fix. Do not treat QEMU as a physical prefetch/cache validator.
Sources: [Intel](https://cdrdv2-public.intel.com/850979/253669-087-sdm-vol-3b.pdf#page=452),
[QEMU Multiboot kernel support](https://www.qemu.org/docs/master/system/qemu-manpage.html).
