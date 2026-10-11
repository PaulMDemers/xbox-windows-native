# USB207 identification and implementation status

The physical unknown device is consistent with an unsupported Xbox XID
controller. A read-only Windows2000 descriptor collector is built, reviewed and
validated against an emulated XID device. It is ready for a controlled physical
collection trial. Full controller support remains blocked on physical descriptor
and report evidence; no controller driver or INF has been installed or delivered.

Source checkout: `codex/xbox-native-usb`, base `47fe46f6189896750ec8972e6ca4486a9072ded1`.
Origin was verified before checkout writes. Canonical evidence remains read-only.

## Established physical evidence

`physical-inventory.json` comes from physical189's preserved after-SYSTEM,
SHA256 `8c87a2577554944e15b976caad8d92ccca9dcd3c4311d78ed6ca62f547f0c9fb`.
Select.Current=1. Five live snapshots agree on the following present devices:

- Two PCI10DE:01C2 OHCI controllers, instances ending `&10` and `&18`,
  service `openhci`, problem 0; two root hubs use `usbhub`.
- Root hub `3&2fe10209&0` has ParentIdPrefix `4&1b2ef565&0`.
  Its port-1 child is USB0451:2046 revision0125, a configured generic hub,
  whose ParentIdPrefix is `5&296d47dc&0`.
- That hub's port-3 child is `USB\VID_FFFF&PID_FFFF\5&296D47DC&0&3`,
  revision0100, problem1, no Service/Driver binding. Its complete compatible
  IDs are `USB\Class_58&SubClass_42&Prot_00`, `USB\Class_58&SubClass_42`,
  `USB\Class_58`. SetupAPI189 records no compatible driver, 0xe0000228.
- Hub port4 has USB1BCF:0005 revision0014, HID class03/subclass01/protocol02,
  HidUsb and mouhid, live problem0. Historical Razer1532:021E composite and
  keyboard/mouse interfaces are persisted but absent from the five live
  snapshots. Do not confuse historical nodes with attached devices.

The XID-compatible class and stable revision argue against treating FFFF:FFFF
as a generic enumeration-failure sentinel. Both XBCD's exact ID table and
Xb2XInput's original-controller list include this VID/PID. This does not prove
the identity/model, full raw descriptors, endpoints, report lengths, or input
behavior of Paul's device. No physical raw USB descriptor capture was found
in the pinned evidence. The earlier Xromwell/Razer hang remains separate.

## Implementation

Original `probe.c` uses classic Windows2000 hub IOCTLs to collect complete
live IDs/compatible IDs, CM parents/status, hub interfaces, per-port raw device
and configuration descriptors, child hub names and driver keys. It makes no
binding, reset, policy or installation change. Per-request 3s timeout,
same-thread CancelIo, 3s completion drain; static memory is never reused if
cancellation does not drain. Process abort is recorded, never counted as success.
Global120s request, hub/port/config/buffer/log limits and external host bound.

`analyze.py` retains raw bytes and rejects malformed/short descriptors. Initial
10,047 synthetic host descriptor mutation/parser/framing checks pass. These are not device tests.
Build007 passed compilation with warnings treated as errors, i386/subsystem5.0
PE review and resolution of imports against the actual owned NT5 DLL exports.
Binary SHA256: `b79d517414d588947432705d9089348ac66711a3a4de44497139293552d9e5b1`.
Source SHA256: `bc5a5a479686efe77c9f54a20dacb756bd00b86e91935bf112c126c9a275ac46`.
Cancellation/timeout paths received source review; no fault-injection claim.

## Emulator result and retained failures

Emu003 completed the collector in27.210s:75 present device nodes,4 hub
interfaces,15 ports,5 complete configurations,36 IOCTLs. The XID Duke model
045e:0202 returned class58/42/00 and interrupt endpoints82/02, maximum packet32,
interval4. Its configuration was0, with zero open pipes and no driver binding.
Keyboard and mouse configurations were03/01/01 and03/01/02 respectively.
Their device nodes used HidUsb and kbdhid/mouhid with problem0; this establishes
enumeration and binding only. Raw bytes and decoded structures are preserved
in `emu003/observation.json` and the private `artifacts/emu003/usb.log`.

One request failed: IOCTL34, GET_NODE_CONNECTION_DRIVERKEY_NAME, error2 on
hub7916/port1 (the unbound XID child). All descriptor requests succeeded. The
audit allows this exact reviewed absence and does not relabel the log as having
zero failures. The collector's code returns2 for this recorded query failure.

The desktop/keyboard/mouse screenshots are visibly scrambled and do not
substantiate any input or display success. Their exact cause is undetermined.
The observer used monitor pause/resume for capture, then stopped its own emulator
from the host. These are diagnostic observations, not normal boot/shutdown or
cold-boot persistence qualification. No physical console was accessed.

Cold audit after host stop:319 directories,6716 files,320 directory clusters,
zero allocation errors and zero orphans. All28 protected file comparisons
matched, including the collector and USB/HID providers. All five registry hives
walked successfully with valid checksums and equal sequence numbers. SetupAPI
retained its complete prior byte prefix. These checks do not establish a clean
Windows shutdown. See `emu003/audit.json` and `emu003/runtime-review.json`.

Retained unsuccessful attempts: build001..005 busy build-lease refusals;
build006 missing winioctl.h; first preparation rejected a Windows relative path
before image creation; emu001 closed before Windows launch on a loopback FTP
greeting EOF; emu002 closed after an orphaned manually-created xemu XID model
asserted without ControllerState; emu003's initial port preflight refused ports
occupied by another workstream. No other emulator was controlled. Emu003 used
the normal xemu keyboard/controller binding path and case-specific loopback
ports4834/4836 under exclusive xemu/xemu-ui leases. Every owned run is closed.

## Driver direction and qualification limits

Do not bind this XID interface to Microsoft's ordinary HidUsb: its class is58,
not03, and no HID report descriptor has been captured. The actual baseline uses
SP4 openhci/usbd/usbhub/HidUsb providers, not ReactOS USB code. A supported
implementation needs a USB-to-HID gamepad minidriver or equivalent real input
interface with explicit endpoint/report validation and lifetime ownership.

XBCD upstream `0459aecb020faf85b918680d7dcd5fa49b6b9036` is a useful GPL-2.0-or-later
reference and includes FFFF:FFFF, but is not a reviewed drop-in candidate:
SendAwaitUrb waits indefinitely; cancellation, timer/DPC and remove ordering
need a complete lifetime audit. No third-party driver source or binary is
imported into the authored package. The separately attributed RemoveLock.c
requires its own license review before reuse.

The pinned xemu build (SHA256685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890)
contains XID Duke/S models. Its XID source files match the original build manifest;
Duke is045e:0202, S045e:0289, class58/42/00. Emulator descriptors and input are
model behavior, never qualification of the physicalFFFF:FFFF controller.

No durable controller driver binding, input, cold-boot wizard elimination or
physical qualification is claimed. The concrete next step is coordinator-owned
physical collection under `HARDWARE-PROTOCOL.md`, followed by separately reviewed
vendor-request/report transport and an NT5 USB-to-HID minidriver with bounded
URBs and cancel/remove lifetime handling. The standard hub API cannot issue the
vendor XID request or read interrupt reports. The collector supplies the first
missing evidence without pretending to solve that transport requirement.

`package.py` gates the diagnostic ZIP on binary/source pins, actual NT5 import
review, complete descriptor capture, the exact explained missing driver key,
protected hashes, cold allocation, hive integrity and preserved SetupAPI history.
It packages authored source/parser, executable, evidence summaries and physical
collection protocol. Binary/media artifacts remain local; only source/reports
are committed to the assigned branch. No main merge or release tag is made.
All physical0101/video0093,0088rollback,immutable0.1.0 and failures preserved.
