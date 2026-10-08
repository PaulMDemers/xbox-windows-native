# Closed failed observer: premature API code pin

candidate001 reached probe entry before its page was GDB-readable. One real CPU
fault/step/re-entry made it readable, and the exact relocated probe entry matched.
The observer then prematurely read future kernel32 API code and received E14.
250 pins/full display text and probe entry were retained, but no CreateFile return,
exit or rendering checkpoints. Full teardown/resume succeeded, then explicit
failure stop. No normal shutdown or workload success is claimed.

Cold results repeat the failed unclean state: no log/reference files/events,
normalshutdown0, consistent allocation325/6758/326, protected/payloads unchanged,
SYSTEM hive structural parse failure, other4 hives parse. No physical changes.
Never relaunch/recollect. New scanout3 pins API text only at actual execution,
uses bounded real-fault/re-entry deferral, reads pathname only after API return.
