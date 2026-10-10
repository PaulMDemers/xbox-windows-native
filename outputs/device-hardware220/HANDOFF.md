# Serialized device hardware work

The user authorized the existing audio, USB and PCI chats to conduct their own
hardware testing on October 10, 2026. This supersedes the coordinator-only
physical restriction in the historical device-workstreams207 handoff. The video
coordinator remains emulator-only during this queue. No branch merge is implied.

One console: audio first, USB second, PCI third. Only the current owner may
contact console FTP, alter startup/configuration, deploy or launch. Others can
prepare independently. Run `python queue.py claim audio|usb|pci` here before
physical access. A claim persists through process exits, crashes and chat pauses.
Do not remove or overwrite claims. Release only after collecting evidence,
restoring normal startup and the captured incoming driver/configuration baseline,
readback verification, and confirming dashboard return. Then run
`python queue.py close NAME --report ABSOLUTE_REPORT_PATH`. If console restoration
or user input is pending, retain ownership and record it in the report.

Use the supplied credentials through XWN_FTP_HOST/USER/PASSWORD, never in reports
or committed files. The Razer keyboard is always unplugged during Xromwell; the
user has authorized launches without another keyboard confirmation. Record each
accepted launch once; never relaunch from a timeout assumption. If necessary ask
once for actual screen state. Preserve failed evidence and installed rollback.

Before any change, snapshot and hash actual incoming boot files, startup, service
and driver state. Preserve FATX0101/video0093, original0088 and immutable0.1.0.
Do not deploy the video coordinator's exploratory219 boot-video candidate or
mix other device candidates into a trial. Restore your own incoming baseline
before releasing the console. Use unique remote/local trial paths and bounded
tests, real application/device evidence, normal shutdown and available cold
integrity/event checks. Keep user observations, emulator results and physical
results distinct. Never suppress events or disable devices to obtain a pass.

Audio: use the reviewed experimental ACI package and trial/rollback protocol;
physical codec/output is unqualified. USB: first collect actual descriptors and
input reports with existing stack, without replacing controller stack. PCI:
identify and safely probe devices first; unresolved shared SMBus/HAL/video and
AC97/audio ownership forbids speculative functional writes. Each chat reviews,
checks and commits/pushes its own source/reports on its existing branch.

Runtime queue state is private host coordination data in state/. Its report links
are consumed by the coordinator; a closed ticket permits the next chat to claim.
