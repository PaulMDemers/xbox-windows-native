Before bootstrap, runtime freeze was requested while candidate preflight19579 was
still running. It rejected the absent candidate preflight JSON; initial Run.ps1
then rejected absent emulator-ready.json before creating runner-start or a guest.
Preflight completed ONCE; the same unmodified source freeze subsequently succeeded
and ONE control bootstrap/Windows request occurred. No repeated preflight, physical
access, guest launch or mutation arose from these host refusals. Frozen sources/
snapshots remain unchanged. Inspect actual launch and cleanup records for outcomes.
