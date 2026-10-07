# Correct bound display selection before testing unchanged DDI

Fresh immutable child of the same sharedUC0106 parent. Same0107DLL, same113probe,
same drivers, settings and emulator policy. Never reuse the failed old child.
The sole correction is including the GPU class Settings subkey in selection;
exact logical hive comparison requires precisely two changed selector values.
Current control set only; LastKnownGood and unrelated devices remain intact.

Compare against the already closed strictPASS video-direct-ddi/control001,
whose parent, payload bytes, startup and protected hashes must match. Expected
marker differs0/1, and only SYSTEM hive differs. All54drawing/162pixel checks,
identity, normal shutdown, cold allocation/hives/hashes and strict event gates
remain. No driver compilation or speculative escape change. Require the actual
custom identity before calling the authored display active.

The old candidate remains failed: identity0, no workload or normal restart,
post-timeout diagnostic shows original framebuf loaded. Its narrow configuration
check missed the class Settings value; all-selector inventory preserves it.
A rendered desktop alone is not evidence of candidate driver execution.
