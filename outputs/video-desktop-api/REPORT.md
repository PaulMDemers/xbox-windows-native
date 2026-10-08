# Exact desktop result resolved; workload failure remains preserved

The third temporary desktop was still openable immediately after CloseDesktop
succeeded. This resolves the old log ambiguity: OpenDesktopA returned handle920
for XwnDesktop126_2, not NULL with last-error0. The probe then successfully closed
that reopened handle, restored input, reported its assertion failure and exited7
after requesting a normal restart. No driver patch or assertion relaxation was
made. The first two temporary names were absent after close: NULL/error2.

The observer captured eleven real user32 call/return pairs, fifteen helper
markers, forty-seven stops and seventy-three exact resident byte pins. Arguments,
return values, raw TEB last-error, thread identity and stdcall stack displacement
are independently verified. The same one RAM0109 ownership slot, primary surface
and PDEV/shadow fields persisted across all fifteen markers. None of the nine
watched driver lifecycle functions fired over the three create-through-close
intervals. This is bounded negative coverage, not surface recreation qualification.

The observer now catches the helper's actual ExitProcess, removes every breakpoint
and resumes before normal guest shutdown. The supervisor waits for observer
closure before terminating the owned emulator after dashboard return. This run
has verified teardown; the old connection-reset/unfinished-teardown failure is
unchanged. Seven real-evidence mutations are rejected across API/pin/TEB and
ownership/armed-site checks.

The workload remains strict FALSE: eight exact49152-byte RGB files were produced,
and the final ninth image was never attempted after the assertion failed. Cold
integrity is clean:326 directories,6768 files,327 directory clusters, no errors
or orphans, five parsed hives, unchanged protected files/helper/startup/configuration
and96MiB/1536-cluster pagefile map. There is one normal shutdown and no warning,
error or application event delta. These do not turn the failed workload into PASS.

Microsoft defines CloseDesktop as handle closure; it does not promise immediate
name disappearance. Therefore the test's immediate disappearance requirement is
stronger than this API contract. The actual remaining internal reference owner,
eventual destruction time, and any debugger timing contribution are unresolved.
Do not infer a driver bug, leak, or data corruption from this result.
[CloseDesktop documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-closedesktop)
(accessed2026-10-08).

Unique candidate001 accepted2026-10-08T02:51:34UTC. Preparation76568, runner75589,
tracer54662, supervisor56111 and audit26799 are CLOSED. Never relaunch/recollect.
Guest probe126 and all driver/settings bytes are identical to the previous ordinary
PASS and failed trace. Physical0101/video0093,0088rollback,immutable0.1.0 and the
qualified128GiB recovery/crash-handoff baselines remain unchanged.
