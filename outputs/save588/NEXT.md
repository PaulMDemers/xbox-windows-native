# Active588 phase2: first save persisted, second launch sent

User reported saving, closing/reopening and normal Restart to dashboard.
Fresh after1 paired capture contains /E/xwn588.txt, exactly18 ASCII bytes:
Xbox save test 588. SHA2568800e17235914771753c7af7ce8d57ba407b2b949be8d187a6f054da2d774cb3.
System EventLog6006 delta1; five hives clean/raw checks pass; protected720p,
ordinary launcher and startup unchanged. No temporary hook exists to remove.
Ftdisk49 and Srv2013 remain in new events; no whole-allocation/paging-health claim.

Source review caught audit.py assuming every after-file existed before; no
execution of that version occurred. audit_review002.py handles newly created
files; audit1 and phase1-review pass. Preserve the original and review record.
First phase is collected/audited; NEVER recollect it or resend launch1.

Second ordinary launch sent at 2026-10-19T21:13:31.048719+00:00, reply 200 EXEC command succeeded..
NEVER resend launch2. User asked to reopen C:/xwn588.txt without rewriting,
confirm text, Restart normally and report dashboard. Actual phase2 screen is
not yet observed. Wait for response; if failed, preserve instead of retrying.

After response record observer2.json, run controller.py after2 ONCE through
private C:/xwn588/session.py, then audit_review002.py 2 with installed offline-disk
LD_LIBRARY_PATH as in previous note. Require same exact saved bytes and normal
shutdown delta, user reopen observation and clean hives. No third launch planned.
Leave the small test file on E; no cleanup of unrelated paths. No RCT/GPU claim.
Automation PAUSED. No owned host process remains; console phase2 is OPEN.

# Active588 watched physical file persistence test

The user authorized proceeding on the original development Xbox. Fresh588
baseline captured10 files with paired readback into private C:/xwn588/before;
protected720p and ordinary startup match and /E/xwn588.txt was absent. Five
captured hives pass raw checks. First host audit invocation lacked libhivex
loader path; failure retained, corrected invocation passes on same new capture.
No guest code or startup hook was installed, no FTP file writes, no VM launched.

One SITE EXEC through ordinary E:/Applications/XWNEBoot/default.xbe was sent at
2026-10-19T21:05:50Z and received200. NEVER resend launch1. Actual screen unknown.
The user has been asked to save Notepad text `Xbox save test 588` to C:/xwn588.txt,
close/reopen it, then Restart normally and report dashboard return. Wait for that
observation; a200 or dashboard presence is not Windows or shutdown proof.

Follow outputs/save588/DESIGN.md and fresh actual receipts. After user reports
return: record observer1.json (including actual save/reopen and normal Restart
observations), run fresh588 controller after1 once via private C:/xwn588/session.py.
No hook cleanup is needed because none was installed. Audit1 uses WSL python
with LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu.
Verify actual file contents, normal event delta, hives and protected files before
launch2. Second launch is planned only after first-phase audit; ask user to reopen
same file without rewriting, then normal Restart for final capture/audit2. If
first boot failed, preserve it and review; do not retry until lucky. No RCT claim.

Fresh host admission tests pin request/helper sources; one20-second SITE reply
bound per ordinal. Console ownership uses existing demo251 ticket. Both host
volumes above projected20GiB reserve. Automation remains PAUSED. No owned host
job is active after capture/audit; console launch1 remains OPEN awaiting user.
