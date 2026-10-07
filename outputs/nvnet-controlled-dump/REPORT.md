# Shutdown fixed; dump written to a wrong 28-bit address alias

Crash003 is CLOSED. The intendedE058D103 and all four cookie parameters matched.
Resident pins show NVNet0104 shutdown entry, idle-helper entry and a paired
shutdown return, followed by callback-scan return. The previous nestedD1 did
not recur at that boundary. The observer then exhausted its64-event limit on
the same pre-dump breakpoint because it was not removed after the first hit.
All breakpoints were removed and the guest resumed. After30seconds the screen
said physical memory dump complete. This observer failure is preserved.

Cold evidence rejects dump qualification. The intended absolute disk offset
148440145920 still beginsPAGEPAGE. At offset11001192448, exactly2^37 bytes lower,
the disk now containsPAGEDUMP and the exact intended bugcheck/cookie. Nine block
writes target that alias;57456 bytes of the inspected64KiB region changed.
See alias-verification.json. The precise truncation producer is not yet known.
No recovery child was booted from this corrupted-address result.

The metadata allocation audit remains clean324directories6756files325directory
clusters, five hives parse and selected protected hashes match. Those checks do
NOT establish that every file's contents were unaffected by the misplaced dump.
Zero normal shutdowns is expected for this deliberate crash; ordinary PASS is
never claimed. Dump write qualification is FALSE despite the completion screen.

The new dump-lba-trace/crash004 diagnostic removes one-shot breakpoints, observes
the real write callback's64-bit offset/source header and final dump return,
and traces ATA port/command writes. It changes no guest driver or setting.
Keep physical0101/video0093 and0.1.0 unchanged. All testing remains emulator-only.
