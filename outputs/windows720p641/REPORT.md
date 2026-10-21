#641 CLOSED: ordinary720p control passes observed desktop/restart scope

After640 failed before producing its interactive receipt, this fresh control
launched the unchanged ordinary E:/Applications/XWNEBoot/default.xbe. There were
no test hooks or remote file writes. One SITE request was accepted at
2026-10-21T03:43:27.013357Z. The user confirmed the Windows desktop, then initiated
Start > Shut Down > Restart. The dashboard became reachable at135.5seconds;
27 selected files were collected with repeated exact readback.

One new EventLog6006 confirms normal shutdown. Protected files are unchanged,
five registry hives parse and event history is preserved. Ftdisk49 remains,
so strict_passed is false. The host observer exited0; console is at dashboard.
No hook is installed. No full physical FATX allocation scan was performed.

This confirms the ordinary720p path still boots and restarts. It does not prove
that480p caused640's failure: mode/launcher and preceding boot history differ.
It does not qualify physical480p typing or save/reopen, which remain untested.
The earlier638 watched480p drawing result and639 emulator interaction result
remain separate. Boot intermittency is not diagnosed here, and no driver change
or supported boot-mode selector is promoted. Never rerun/recollect this control.
