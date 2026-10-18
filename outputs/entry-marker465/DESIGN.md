# Contract

marker_guarded takes a pointer to an owned writable 96-byte record and requires a
valid owned stack. It preserves the general registers and restores EFLAGS. A
terminal record cannot be rearmed through this interface. There is no kernel,
disk, EEPROM, allocation or thread API in the helper.

Status reads are 16-bit at c000. Writes are restricted to c004 (SMC write address
0x20), c008 (command 8 then 7), c006 (pattern then 1), c002 (start 0x1a), and c000
(acknowledge only completion 0x10 while not busy). Unknown/error bits refuse.
The record exposes counts, statuses, timestamps and partial progress. Success
means acknowledged transactions in the observed implementation; a human-visible
physical light still requires a hardware observation.

The host uses SIGSEGV instruction emulation and PR_SET_TSC. It models privileged
interfaces explicitly. Actual interrupt disabling/restoration and device behavior
remain outside that host proof.
