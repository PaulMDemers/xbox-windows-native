# Physical inventory 418: launch accepted, return pending

The user confirmed the existing XWNEBoot demo booted and worked, then manually
restarted to the dashboard. No benchmark was queued and no command window was
expected. This is a user observation of the existing demo, not the inactive416
rebuilt loader. No416 activation record exists.

The user authorized inventory deployment and launch. Stage001 failed FTP login
before file access; stage002 authenticated but failed a host baseline-record path
lookup before console writes. Both records and original script revisions remain.
Stage003 uploaded the reviewed417 build002 utility to the previously absent
E:/Applications/XWNInfo/default.xbe and read back exact bytes. All selected416
protected non-registry files were unchanged before and after staging. The script
uses the existing demo251 ownership ticket and console ownership marker.

One SITE EXEC was sent at2026-10-16T21:46:10.772134Z; response200 accepted. This
does not prove execution or completion. A subsequent collection command timed
out connecting to dashboard FTP; it exited without collecting or creating a
collection record. The user was asked for the current screen before restart.
Do not repeat the launch. No report, visible summary or automatic dashboard
return has been verified yet. No Windows launch or loader activation occurred.

On dashboard return, run physical.py collect with the authorized FTP environment.
It requires exactly one fresh numbered report, validates its schema and repeated
readback, and checks the selected protected baseline. If no fresh report exists,
preserve that failure; do not relaunch automatically. A successful report would
qualify only this inventory on this console, not another revision or full storage
integrity. No console C access, Windows configuration changes or firmware writes.

All host commands have exited; no observer or other owned process is running.
No physical screen outcome is inferred from the FTP timeout.
