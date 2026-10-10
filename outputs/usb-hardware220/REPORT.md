# USB220 authorized physical trial

Status: PREPARED, WAITING; USB claim refused because audio has not closed its restored
baseline. No USB physical access, writes or launch has occurred. No owned guest,
FTP connection or background controller exists. Shared queue: canonical
outputs/device-hardware220/state; order audio, USB, PCI.

Preparation completed: unchanged build007/source pins verified; host scripts
parsed; five offline fault checks passed for no socket before ownership, no
socket after queue closure, no repeated uncertain launch, interrupted startup
write restoration, and startup restoration before a failed result read.
Frozen controller and dependency pins are in prepared.json. The shared
state/usb-status.json links this report without claiming or releasing a ticket.
The original preparation is preserved as prepared001.json. The current revision
adds guards from audio's fresh, successful capture002 for the legacy ACI and
supporting audio drivers; actual incoming bytes still require USB's own capture
after audio's restored-baseline closure. No candidate audio bytes are adopted.

The October 10 user authorization and new220 handoff supersede the historical
coordinator-only restriction in USB207. This trial uses the unchanged reviewed
USB207 build007 collector, commit5d86c99870e977f807d9a47ee75f6792e349cdbe.
Binary SHA256 b79d517414d588947432705d9089348ac66711a3a4de44497139293552d9e5b1.
This is standard device/configuration descriptor collection through the existing
NT5 OHCI/hub stack. It does not install a driver, configure the XID child, read
vendor XID descriptors, or capture unbound XID interrupt reports.

Source/report root:
E:/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/usb/repo/outputs/usb-hardware220

Unique planned remote trial directory: /F/xwnusb220a. Windows path: C:\xwnusb220a.
Private snapshots and rollback: artifacts/physical001. Mutable trial record:
physical001.json. Raw captured hives/logs remain private. Capture actual incoming
startup, five registry hives, events, SetupAPI and all protected loader/HAL/FATX/
video/network/USB/HID files before staging. Historical211 fixed hashes are guards,
not substitutes for new incoming readback. Preserve0088 and immutable0.1.0.

Launch at most once. Record intent before SITE EXEC; timeout never permits retry.
Collector bounds match reviewed207. Normal restart is manual for this diagnostic;
screen/restart method must come from the user and event/return evidence. Keyboard
remains unplugged. No wizard actions, device disabling, event suppression, HAL,
MMIO, interrupt ownership or GPU changes. No speculative AC97/SMBus operations.

At dashboard return restore startup FIRST, collect every available result and
post-run hive/event state, walk the hives offline, then restore exact incoming
registry snapshots and verify all protected files plus dashboard identity.
Keep the queue ticket while restoration or user input is pending. Close only
with an actual restored-baseline declaration and this report path.

Full physical allocation integrity, repeated cold boots, controller input and
driver installation are not established by the descriptor trial. All earlier
USB207 failures remain preserved. New failures will be retained in trial records.

Preparation commit4680a5e5e48d07168a546c31c8b6332d04f1ba5c is pushed and remote-verified. The repository scan passed for19279 tracked files. Scan session11374 and commit/push session84317 are closed. No owned session remains.
