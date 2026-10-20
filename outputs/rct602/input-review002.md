# Host input corrections before the single game launch

The native Display Properties screenshot confirms1024x768 HighColor16bit.
The first open-display dispatch rejected stale attempt599 before sending input;
actions002 corrects only that literal. The original receipt/source remain.

The initial copy plan and a focus/Ctrl-A attempt returned transport success but
did not show the intended command. Escape followed by a fresh Run dialog selected
the old command. The corrected copy command was visually confirmed before one
Enter. It completed and closed normally; its failure branch would have paused.
The guest verifier's502-file result must still pass the subsequent cold audit.
Both CDs were then ejected, with QMP block-device responses retained.

A direct PowerShell-to-WSL argument lost the backslashes in the helper path;
the private input receipt shows `C:xwn602-kitrun602.exe`. No Enter followed it.
run-path002 used the JSON dispatcher to preserve backslashes, but Ctrl-A did not
replace the existing text. Its screenshot shows concatenation, not a launch.
No claim is made about whether that was an edit-control contract or timing issue.

Escape/reopen selected the prior command. run-path003 then typed the exact
helper path through the JSON dispatcher. An immediate screenshot still showed
input in progress; a later screenshot confirms `C:\xwn602-kit\run602.exe`.
Only then was one Enter sent. The helper console and RCT startup screens appeared.
No additional helper or game launch was sent. Input submission alone is not
evidence that the guest accepted the intended text or acted on it.

Private evidence: phase1/input-*.json and screen-1792466715277175099.png
(the final path), screen-1792466738889904625.png (helper/game loading), and
screen-1792466752342729811.png (RCT startup). All screenshots remain private.

After the VM exited normally, an already queued host screen command encountered
the closed-state assertion in vm.py before opening QMP. It produced no screenshot
and did not reopen the runtime. The lease wrapper returned0 despite the Python
assertion; the captured traceback, rather than the wrapper exit status, establishes
that rejection. The single subsequent cold readback is separate from this UI call.
