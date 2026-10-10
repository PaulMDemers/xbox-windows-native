# USB207 handoff

October10 update: hardware testing is now authorized through the serialized
device-hardware220 queue. The new trial/report is ../usb-hardware220/REPORT.md.
The hardware220 descriptor trial is complete; the actual child is FFFF:FFFF with XID interface58/42/00 and IN0x81/OUT0x02. Incoming baseline restoration and all three allocation scans passed. Controller input, normal-shutdown durability and strict events remain unqualified. See the220 report and completion.json.
The historical coordinator-only restriction below is superseded for that trial;
the original207 evidence/package remains immutable.

Build007 and emu003 descriptor collection review passed. All owned processes
and sessions are closed. No physical console access occurred. No message to
another chat was sent. Source branch: codex/xbox-native-usb.

Use REPORT.md, package-review.json and HARDWARE-PROTOCOL.md. The next required
evidence is a coordinator-owned physical descriptor capture of the actual
FFFF:FFFF child, followed by separately reviewed vendor XID/report capture.
Do not claim a driver is installed, gamepad input works, keyboard/mouse input
is validated by screenshots, or the unknown-device wizard is fixed.

The emulator images are private and retained on E:. Raw log and after-hives
are under artifacts/emu003; startup/seed/rollback evidence remains preserved.
No automatic retry, physical deployment or cross-chat follow-up is scheduled.
