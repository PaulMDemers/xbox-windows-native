# Physical Notepad persistence588 — passed

On October19, 2026, the original development Xbox completed the two planned
ordinary720p Windows launches. No drivers, boot files or startup hooks were
changed; no test helper was installed and no host FTP file writes were made.

| Step | Observation | Independent evidence |
| --- | --- | --- |
| Before | New test filename absent | Fresh paired dashboard capture, baseline and five hive checks |
| First Windows session | User saved, closed and reopened the file, then restarted | after1 contains exact18-byte text; EventLog6006 delta1; five hives clean |
| Second Windows session | User confirmed same text after boot, then restarted | after2 bytes/hash unchanged; EventLog6006 delta1; five hives clean |

The file is Windows `C:\xwn588.txt`, dashboard `/E/xwn588.txt`, containing exactly
`Xbox save test 588` without a trailing newline. SHA-256:
`8800e17235914771753c7af7ce8d57ba407b2b949be8d187a6f054da2d774cb3`.
The small file remains on the console. Protected720p, ordinary launcher and
startup checks passed after both restarts. Final dashboard FTP capture and the
user's report agree that the console returned to the dashboard.

This qualifies the tested plain-text save/reopen/normal-restart sequence on the
original Xbox. It does not qualify RCT saves, another Xbox, long-term boot
reliability, full FATX allocation integrity, paging health or GPU acceleration.
Ftdisk49 and Srv2013 remain in the system logs. Typed-hive decode limitations
remain explicit in the raw audit receipts; no errors were hidden or waived.

Preserve the first audit invocation's missing libhivex loader-path failure. A
source review caught the original audit's assumption that every after-file
already existed before; the corrected review handles the newly created file.
The original audit was not executed. No closed runtime was recollected.

Evidence: final001.json, observer1/2.json, after1/2.json, audit1/2.json,
phase1-review.json, launch1/2.json and the retained before/host/source receipts.
Private file/hive/event captures remain in C:/xwn588. The sequence is CLOSED;
no third launch, no owned host job or temporary startup hook remains. Automation
stays PAUSED. Next useful package validation is inventory and a watched first
Windows boot on another Xbox when one is available. The delivered ZIPs remain
unchanged and exclude RCT.
