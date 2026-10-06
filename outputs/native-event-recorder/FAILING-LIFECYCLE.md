# Captured first-install shutdown failure

The fixed three-run batch uses independent copies of the same first-install
seed, the same recorder executable, and no debugger or paused screen capture.
The physical console is unchanged. See `batch-summary.json` for all outcomes,
including clean runs, and `batch-review.json` for checked event identities.

## Case 003: failure captured

The cold event log contains one rundll32 DLL-initialization popup with the
window-station-shutdown message. The host records 425 events, all with matching
site bytes, through kernel shutdown. The two hard-error entry points describe
one error, not two popups. The process identity is EPROCESS `0xff9f9020`, PID996;
the hard-error thread is `0xff9a51e0`.

| Event | Tick | Recorded boundary |
| --- | --- | --- |
| 324 | 10035 | CSRSS requests termination of the preceding GPU installer |
| 327 | 10043 | PnP's wait for that installer returns zero |
| 329 | 10043 | PnP calls creation for the PCI1B36:0005 installer |
| 331 | 10044 | Services reaches the resume-call boundary for the new process |
| 332 | 10044 | Creation returns success; PID996; saved token remains `0x8ac` |
| 334 | 10044 | CSRSS reaches another resume-call boundary for the same process |
| 336–337 | 10049 | That installer raises `0xc000026b`, through Ex/ExpRaiseHardError |
| 338 | 10050 | win32k reaches termination call with current-process handle and `0xc0000142` |
| 339 | 10050 | NtTerminateProcess resolves that same target with `0xc0000142` |
| 340 | 10050 | The matching process enters exit handling |
| 341 | 10050 | PnP's wait for the placeholder installer returns zero |
| 344 | 10053 | First recorded PnP shutdown control5 arrives |
| 424 | 10238 | Winlogon enters kernel shutdown |

Resume sites are pre-call observations; they do not themselves prove successful
resume returns. Subsequent execution by the identified installer does establish
that it ran. The event log independently records the same error text. The exact
GUI shutdown-state transition was not recorded; kernel shutdown occurs later.

The successful creation and unchanged sampled token distinguish this failure
from clean002, where services requested termination during failed creation,
the sampled token became zero and CreateProcess returned invalid handle6.
The failing003 installer reaches the GUI shutdown rejection before PnP receives
its shutdown control. A fix that acts only when that control arrives would be
too late for this observed run. This does not disprove a separate token-lifetime
race, nor does it identify the physical console's failing device.

## Case 004: clean comparison retained

This independent copy records 424 verified events through kernel shutdown.
The placeholder creation call is event329/tick9911 with saved token `0x8e0`.
PnP control5 is event331 at the same tick. Creation returns false at
event335/tick9921, last-error6, with sampled token zero. There is no hard-error
record and no cold popup. This reproduces the earlier002 clean outcome under
the same conditions that produced the003 failure. It does not qualify a fix.

## Case 005: no placeholder creation observed

The final independent copy records 419 verified events through kernel shutdown.
The GPU installer's wait returns at event333/tick9999. PnP control5 follows at
event334 in the same tick. The trace contains no placeholder creation call and
no hard-error call, and the cold event log has no popup. This is a third outcome;
it must not be described as another invalid-handle creation failure. The exact
branch that avoids further creation was not instrumented.

The initial report checker incorrectly required a placeholder creation call in
every case. Its source and failure are retained as `review-batch-initial.py` and
`batch-review-initial-failure.json`. The revised checker represents this absence
explicitly and requires a valid trace through shutdown, observed GPU creation
and PnP shutdown control, no hard-error record and no cold popup. No emulator
launch or cold scan was repeated to correct this analysis-tool assumption.

## Next implementation question

Determine why the first GPU installer stays outstanding until shutdown despite
successful cold installation records. Distinguish a pending reboot/removal
decision or installer dialog from an unfinished driver operation. Use a bounded
read-only wait/dialog inspection and matched SetupAPI evidence, then choose an
installation flow that completes before requesting restart. A mere longer sleep
or automatic dismissal is not evidence of completion.

Any change must preserve device enumeration, report installation failures, and
be checked on an ordinary recorder-disabled first-install run plus a subsequent
boot. Keep the existing failed fixture as the control. Do not remove the QEMU
placeholder or suppress its hard error to manufacture a clean outcome. Faithful
emulation of the Xbox memory-controller function is a separate work item.

No synchronization patch or new hardware candidate is supplied by this batch.
The physical popup and Srv2013 warnings remain open. Graphics work can advance
under its own gates without repeating this emulator reproduction indefinitely.
