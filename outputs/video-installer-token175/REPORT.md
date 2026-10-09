# Supplied token becomes invalid during successful inner creation

SINGLE launch2026-10-09 01:06:30UTC→dashboard01:08:54. Owned runner81996,
tracer18800,supervisor55584,cold audit90648 CLOSED.180events/179 resident pins,
27 process creation/return pairs and61 native API pairs; exact ETHREAD and
disassembly-verified stdcall deltas. All breakpoints removed/resumed, no pending
returns. Capture complete in declared scope;40 frozen input/source pins exact.

01B0 outer creation succeeds with actual child loader entries. Later01B4 attempt
from services.exe PID208, one outer frame/thread/command:

-tick6589: UMP supplies token1864; ADVAPI NtQueryInformationToken class12,
  length4 succeeds, output00000000. Matching resident caller/NTDLL bytes pinned.
-inner CreateProcessInternalW begins at6589; its observed closes are1876 and1884,
  not supplied1864. NtSetInformationProcess class5 succeeds. InnerTRUE at6593,
  returned PROCESS_INFORMATION1876/1884/child900/thread932.
-tick6593: ADVAPI NtQueryInformationToken(1864,class8,length4) returnsC0000008
  STATUS_INVALID_HANDLE. This is the first non-sizing failure in this outer call.
  Captured native status differs from Win32 LastError (still0 at API return).
-cleanup closes1876/1884 successfully; outerFALSE at6594, LastError6.

The supplied token was valid before inner creation and invalid afterward. No
same-thread close of1864 was captured within these outer calls.85 other-thread
native API address-lead hits were excluded; they contain no decoded close args.
Do not infer absence of a concurrent close, exact closing actor, token handle
reuse, or corruption in graphics/storage. Numerically aliased handles in174 are
separate runtime evidence, not this run's returned handles. No speculative patch.

Native pairs:37 token queries (21success,15 BUFFER_TOO_SMALL sizing responses,
1 INVALID_HANDLE failure),17 closes success,4 token duplicates success,3 process
information updates success. Buffer sizing errors are retained; they are not the
fatal-token failure or an event-log waiver. Exact status names confirmed in owned
NT5 headers. Six actual-function identity/resident-byte host checks PASS.

Guest5samples/20copies/25timedloops/50 fullscan RAM-FB RGB coherence PASS; normal
shutdown/dashboard, full cold322dirs6721files323clusters0errors/orphans,5hives,
protected binaries/startup exact. StrictFALSE sole exactFtdisk49; no popup or
application-event delta in THIS debugger run. This does not fix174/172 popups;
error6 occurred without popup here, so don't equate those error producers.
No driver/settings/device/UI/service/dump/cache change or physical access.

176 fresh discriminator allows same-process matching token close from another
thread and adds actual kernel NtClose during the active outer interval. It keeps
exact thread/stack pairs even at shared kernel return addresses; foreign frames
excluded and pending pairs must complete. All previous cases remain closed;
physical0101/video0093/0088rollback/immutable0.1.0 unchanged.
