# Observer failure preserved; no crash qualification

Single crash001 CLOSED. The new observer correctly discovered the actual kernel
using both IDT gates, but pinning the fixed-image probe entry raised an exception:
the PE has no relocation directory. All breakpoints were removed and guest
execution resumed. No intended bugcheck was observed and no dump was written.

The inherited supervisor captured/closed30 seconds after the entry-time failure,
before the helper's35-second wait and flush/trigger sequence finished. The image
shows the Windows desktop, not a crash screen. The cold intent stops at
DRIVER_READY; WAITING_30000_MS, with no TRIGGER_ONCE. This attempt must never be
relaunched or used as a recovery parent.

Cold audit fails:12 orphan clusters and4 errors in WMI repository file chains.
These were observed after the host ended an active session before the intended
flush/crash; they are not waived or attributed to a driver defect by this test.
Five structural hives and protected/payload/startup hashes pass; no warning/error
events; unchanged pagefile chain and28-bit alias. Both prefixes remain PAGEPAGE.
failure-verification.json rechecks the frozen script, actual fixed-image PE,
closed disk and explicit failed evidence. No ordinary or physical qualification.

Fresh video-ram-crash2 handles absent relocation tables and tests that exact pin
implementation against fixed-image and relocated binaries. Its supervisor waits
90 seconds on observer failure,30 on real dump return. Guest helpers/drivers and
all success gates remain unchanged. Earlier failure remains immutable.
