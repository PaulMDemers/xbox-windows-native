# Coordinator-only experimental ACI trial

This is a preparation protocol, not evidence of physical qualification. The
audio chat must not contact, deploy to or launch the physical console. Package
creation is gated on the recorded ordinary emulator installation and subsequent
installed-driver playback checks. The original coordinator serializes deployment.

## Scope and prerequisites

Target only the observed PCI ACI10DE:01B1, subsystem00000000, revisionB1, instance
ending2&ebb567f&0&30. The separate01B0 APU remains unsupported. No driver or INF
matches01B0,01B4, USB or other PCI functions. Initial output is analog stereo,
48kHz16-bit. S/PDIF/HDMI-adapter output, microphone, hardware mixer controls and
protected-content playback are outside this package's validated scope.

Before staging, confirm the current console is the intended owned Xbox and is at
the dashboard. Independently resolve dashboard paths versus Windows drive letters.
Verify the currently working loader/kernel/display/network/storage payloads and
startup against the coordinator's current manifest, not an assumed old version.
Preserve physical0101/video0093, original0088 rollback and immutable0.1.0. Keep the
keyboard unplugged through Xromwell as required by the established boot protocol.

Make a fresh, separately named, read-back-hashed rollback bundle before changing
anything: all five SYSTEM/SOFTWARE/SAM/SECURITY/DEFAULT hives and their companion
logs, startup, existing audio drivers/INF/PNF files, current relevant PnP/service
metadata, SetupAPI log and system/application event logs. Record absent target
files as absent. Retain a directory inventory of WINNT/inf so newly created OEM
files can later be identified exactly. Do not overwrite earlier rollback bundles.

The package has separate install and verify directories. Use unused case-specific
guest namespaces; each helper uses CREATE_NEW logs and refuses reuse. Record every
staged path, SHA256 and readback. Do not copy any emulator hive, null binding,
event log, device policy or disk image to the console. The installation must use
the supplied exact-ID INF through actual Windows SetupAPI.

## Installation boot

Set a one-shot startup to the staged physical installation runner, after saving
the exact previous startup. Its directory must contain install.exe, xwnaci207.inf,
xwnaci207.sys and wizard.exe. The runner uses only the known physical wizard
policy, joins its child, observes real setup idle, joins the genuine installer,
observes idle again and requests an unforced Windows restart. It does not waive
an unidentified dialog, a failed installation or a pending child.

Launch exactly once and record requested/accepted/uncertain status and time.
A timeout never authorizes relaunch. On a held dialog or crash, preserve its exact
text and available evidence, and stop the installation verdict. A returned
dashboard is necessary but is not by itself installation success.

On dashboard return, first restore normal startup so the installer cannot rerun.
Collect install207.log, install-runner207.log, wizard201.log, all five cold hives,
SetupAPI history, event logs, installed driver and the actual newly selected
OEM INF/PNF. Independently verify the exact ACI service is xwnaci207, demand-start3,
kernel-driver type1, error-control1, and ImagePath names the intended driver. Match
driver and INF hashes to the package. Preserve all before/after history. Require
one normal Windows EventLog6006 and complete cold storage/hive integrity checks.

## Subsequent playback boot

Do not reinstall or edit the device/service registry between boots. Stage the
separate verification directory and a new one-shot startup. It contains the
physical playback runner, state.exe, probe.exe and wizard.exe. The state check
requires a started ACI device, exactly one loaded xwnaci207.sys, no loaded
ac97xnt5.sys and exactly one WinMM render device before the test proceeds.

Use a modest external speaker/amplifier volume. Expect twelve playback cycles:
eight complete two-second tones and four tones stopped early by reset. Left and
right are distinct400Hz/600Hz signals. Record the actual cable/output path and
channel-specific audible result; emulator WAV capture cannot establish physical
audibility. The analog path must be confirmed before any digital-output claim.

Require joined state/probe success, each open/write/reset/unprepare/close result,
exact full-buffer positions, normal restart/dashboard return, persistent binding,
unchanged protected components and independent cold FATX/hive/event checks.
Record exact unrelated wizard cancellations separately. The helper never targets
ACI, but its use means this is not an integrated prompt-free boot. Ftdisk49 remains
a strict whole-boot failure even if the scoped ACI trial succeeds.

## Failure collection and rollback

Restore normal startup first whenever dashboard access is available. Preserve
the failing disk/log/hive/file state before rollback, including incomplete logs
and any signature, installation or restart dialog. A host reset or physical power
cycle is an intervention, never normal-shutdown evidence. Do not suppress events,
disable services/devices, force completion or repeat the launch to seek a pass.

Use the fresh pretrial rollback bundle to restore the exact changed files and
consistent registry-hive/log set while Windows is offline. Restore prior startup
and any overwritten audio file. Remove only new package/OEM files positively
identified by pre/post inventory and hash; never delete an OEM wildcard range.
Preserve a failed copy first. Verify restoration bytes and cold integrity before
the coordinator resumes the established baseline. Leave kernel, loader, video,
network, storage, USB input and dump policy unchanged throughout this audio trial.
