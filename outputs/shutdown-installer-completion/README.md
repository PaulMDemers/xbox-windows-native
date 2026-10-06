# Targeted GPU setup completion diagnostic

Fresh independent children of shutdown-install-idle/fixture-002.json change only
xwnidle/probe.exe. Driver binaries, startup command and staged SYSTEM/SOFTWARE
remain unchanged. The pinned original969a99a8 emulator has no host recorder,
resource-model option, debugger or pause during ordinary observation.

The helper inspects rundll32-owned windows at0/30/60/90/120 seconds. It may send
one normal WM_COMMAND button notification only when exactly one visible/enabled
Found New Hardware Wizard matches the successful GPU device page, success and
reboot-required text, explicit close instruction, and Finish button12325 with
its observed immediate parent. Unknown dialogs receive no action. It also logs
the owned NT5 CMP_WaitNoPendingInstallEvents(0) result. A return of0 at the initial
sample is not a guarantee that later installation will not start.

This diagnostic still requests restart after120 seconds even if an installer
remains pending. It is not a production restart guard or ordinary qualification.
No physical hardware change or deployment is permitted by a diagnostic PASS.

## Case001: no action, clean return, no efficacy evidence

The initial exact text matcher required CRLF; this NT5 control returned LF.
Consequently no GPU_FINISH_ONCE record exists, and the GPU wizard/pending102
persisted through120 seconds. Dashboard return and cold checks passed, with no
popup, but the intended intervention never ran. Preserve001/probe.c and its
probe-review.json as the executed source and build pins. This clean outcome
cannot be credited to completing the wizard.

## Case002: matcher correction

Only CR immediately preceding LF is normalized for comparison. All other text,
class, device, parent, control ID, visibility and enabled checks remain exact.
A fresh fixture tests the corrected action. Observed completion and queue state,
not PostMessage success alone, must establish whether it worked.

If return times out, capture-timeout.py CASE retains one private64MiB read-only
snapshot after the recorded deadline, briefly pausing and resuming the owned VM.
It does not write guest memory. Collection requires owned cleanup and never
repeats an existing audit stage. Host termination is not a normal guest restart.

## Case002 result: Finish works, reboot prompt remains pending

One verified Finish notification was posted at30 seconds. At60/90/120 seconds
the GPU wizard was gone, but the same installer owned System Settings Change,
asking whether to restart now. Pending-install status stayed102. Normal restart
returned to dashboard, no popup, hashes/hives/full F allocation passed. The
queue-idle requirement still failed; this is not a setup-completion solution.
Executed source and build review are preserved under002.

## Case003: defer GPU reboot, gate final restart

A fresh fixture adds one No notification only to the exact observed restart
question, same rundll32 PID whose GPU Finish was posted, with both Yes6 and No7
buttons visible/enabled and parent checked. All unknown dialogs remain untouched.
After the same120-second observation period, restart is withheld unless the
pending-install API returns WAIT_OBJECT_0 and both targeted actions were attempted.
RESTART_BLOCKED_PENDING_INSTALL is a held test, never a normal restart or PASS.
Source and result records must establish which actions actually succeeded.

Case003 did withhold restart: RESTART_BLOCKED_PENDING_INSTALL258. GPU Finish
and No succeeded; the next wizard belongs to exact command-line identity
PCI\VEN_1B36&DEV_0005&SUBSYS_00000000&REV_00\2&ebb567f&0&03. A post-timeout
snapshot retained64MiB privately and decoded the live shell, zero bugcheck and
1812 resources without an observed exclusive wait cycle. This was held setup,
not the earlier shutdown stall. Host cleanup followed; no guest normal restart.
Cold selected payloads, hives and full F allocation remained consistent.

## Case004: explicit unsupported emulator-device acknowledgement

A fresh fixture adds Cancel only for the exact above command line read through
OpenProcess/NtQueryInformationProcess/ReadProcessMemory, a visible welcome page
with its three exact texts, enabled Next and Cancel buttons and checked parents.
No other device/dialog is cancelled. This deliberately leaves the test device
unsupported, does not remove it or install a fictitious driver, and cannot
qualify its functionality or physical hardware. The restart gate remains.
The first link attempt failed on no-CRT stack probing; static single-threaded
scratch strings fixed that without disabling stack probing. Failure retained.

Case004 passed the targeted setup checks: Finish at30s, defer reboot at60s,
cancel identified placeholder at90s, no installer window and pending API0 at120s,
then normal restart and dashboard return. No new popup or unexpected event error;
selected payloads/runtime files, five structural hives and full F allocation pass.
The placeholder remains enumerated without Service/Driver binding. This is a
completed setup workflow with an acknowledged unsupported device, not a new
hardware capability and not proof that Windows' original shutdown race vanished.

## Subsequent boot validation

The minimal repeat-probe logs to a new repeat.log, waits120 seconds and checks
pending installation before normal restart. It has no window enumeration, button
actions, host recorder or debugger. SYSTEM/SOFTWARE and video trace are retained
from004 without resetting them. Driver binaries and startup command are unchanged.
Case005 failed at host startup: xemu could not resolve its nested relative backing
chain. No Windows launch was requested. Logs/cleanup and original005 disk remain.
Case006 copies the completed004 delta beside its backing parent, rebases that
copy's metadata and requires qemu-img compare success plus unchanged original004.
It does not reset the guest state or discard the failed attempt.

006 again encountered the same placeholder installer and logged
RESTART_BLOCKED_PENDING_INSTALL258. The post-deadline snapshot shows a live
shell and that exact command line, not a bugcheck or observed exclusive wait
cycle. The host then cleaned up; no guest normal shutdown occurred. Cold hashes,
hives and allocation remained consistent. This disproves durable completion by
Cancel alone. Follow-up uses a narrowly matched explicit unused-device package;
see ../shutdown-null-placeholder/README.md. Failed controls remain retained.
