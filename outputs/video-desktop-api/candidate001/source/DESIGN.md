# Exact post-close desktop API result

Use unchanged probe126, unchanged RAM0109 and a fresh child of the same immutable
video-mode-reset prepared fixture. The older ordinary pass and incomplete trace
remain closed and preserved. No new binary build, physical access or policy edit.

Observe all direct probe calls to user32 OpenDesktopA and CloseDesktop, paired by
thread, return PC and exact stdcall stack displacement. Pin owned resident entry
and return instructions. Capture bounded desktop name/access arguments, returned
handle and exact TEB last-error before/after. Derive the latter from the pinned
kernel32 GetLastError implementation: FS:[18] supplies TEB and offset34 supplies
LastErrorValue. Require TEB's self-pointer, retain raw64 bytes and segment state.
Other-process/internal calls are explicitly recorded and stepped, not attributed
to the probe. No guest writes, register edits or synthetic API invocations.

Retain the nine driver lifecycle sites and fifteen desktop markers from the old
observer. At the probe's actual ExitProcess entry record status and pending calls,
remove every breakpoint and resume even on early workload failure. The supervisor
waits for trace-closed.signal and records teardown state before closing the VM
after dashboard return. Bound600 seconds,384 stops,40 captured API calls and64
driver calls. Only resident executed sites are claimed pinned; no full residency.

Do not change the immediate name-absence assertion, infer a driver fault from a
failed helper, or silently qualify an incomplete run. Cold workload, allocation,
all five hives, protected files, nine images, pagefile and strict event gates remain
unchanged. Successful observation of a failure is diagnostic evidence, not an
ordinary or physical PASS. Preserve every result regardless of outcome.
