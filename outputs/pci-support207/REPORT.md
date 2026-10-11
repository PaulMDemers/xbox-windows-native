# PCI support207 — physical inventory complete; SMBus ownership review

October10 update: physical220 completed with normal user Restart, preserved
inventory and verified scoped baseline restoration; its ticket is closed.
See hardware220/REPORT.md for physical findings and ownership001/REPORT.md for
the subsequent offline resource/ownership review and pending build guard.
Historical emulator evidence below remains unchanged.

Owner: codex/xbox-native-pci in the isolated E: checkout. Starting revision
47fe46f6189896750ec8972e6ca4486a9072ded1. HEAD/remote guards verified before writes.
No physical access, deployment, guest policy edit or cancellation performed.

Current milestone: physical IDs/resources and failure mode established; real
SMBus transaction engine passes67617 host cases and two fresh paused xemu model
runs (model003/model004). Constrained kernel003 and full package004 compile;
all 61 imports/dynamic lookups resolve against pinned NT5 providers. Native001
completed actual SetupAPI installation and all six live telemetry cases, then
passed cold integrity checks. It was host-stopped and is NOT shutdown/persistence
qualified. Native002 preserved that binding across a cold relaunch and passed
fresh live telemetry without reinstalling, but held restart on pending setup.
The new SetupAPI history identifies unresolved audio01B0. This is a concrete
integration blocker outside PCI ownership, not a completed shutdown cycle.

## Identification

inventory.py independently opens the pinned physical189 SYSTEM hives read-only,
verifies their captured hashes and joins each current-control-set PCI instance to
its typed class/driver/service keys. physical189-inventory.json retains full
hardware/compatible IDs, locations, bindings, Select and exact appended SetupAPI.
The 19 current-control-set records include stale PC/emulator devices; this is not
a claim that all 19 were physically present. The historical count of 38 included
both control sets.

01B4: `PCI\VEN_10DE&DEV_01B4&SUBSYS_00000000&REV_B1\2&ebb567f&0&09`,
PCI bus0/device1/function1, hardware class0C0500. MCPX SMBus controller.
01C1: `PCI\VEN_10DE&DEV_01C1&SUBSYS_00000000&REV_B1\2&ebb567f&0&31`,
PCI bus0/device6/function1, class070300. nForce AC'97 modem function, with potential
codec/link ownership overlap with audio01B1 at device6/function0. No modem codec
presence or usable telephone interface is established. No audio package edited.

physical189-resources.json and physical189-resource-decode.json decode typed
LogConf records. The root is PCI_HAL\PNP0A03\0, servicepci, parent2&ebb567f&0.
SMBus BootConfig has C000/length16 and C200/length32.01C1 has port256/port128/
memory4096 and IRQ requirements, but no BootConfig. Requirements do not prove a
responding codec or current allocation. Device-private tags identify PCI BAR
groups; the constrained candidate preserves all unrelated groups and tags.

Neither target has a Service or Driver link. Physical189 appended SetupAPI has
01B4 PID92 at06:13:23UTC and01C1 PID964 at06:13:30UTC October9, both
DIF_SELECTBESTCOMPATDRV /0xe0000228, no compatible drivers. Before/after metadata
is unchanged. No installation success or lost previously correct binding follows.
Physical SYSTEM hashes: before50c57a236415155daac77b272b43341446632dd078f5256cfd8c2e167c6ce487;
after8c87a2577554944e15b976caad8d92ccca9dcd3c4311d78ed6ca62f547f0c9fb.

## Implementation and evidence boundaries

smbus.h is an authored bounded byte-data read engine, restricted to SMC AV-pack
and ADM1032 temperatures. It checks both host and bus busy, refuses to disturb an
initially busy transaction, retries collisions at most three times, gives errors
precedence over completion, bounds completion/abort waits, and requires quarantine
after a stuck engine. It never writes a slave, changes fan/LED/power/encoder state,
reads EEPROM secrets or exposes read-to-clear SMC interrupt status.

test-smbus.c drives the actual engine with status combinations, delayed completion,
collisions, busy ownership, timeouts/stuck abort and all 16-bit address/command pairs.
smbus-model.c drove the same engine against a paused, owned xemu qtest model.
Neither file is a Windows driver or a completed persistent PnP fix.

The installed HAL binary a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648
contains HalpXboxPowerAction at0x196c0: CLI, reads0xC000 bit0x800, writes SMC
0x20/address, register2, action, clears status and writes control0x1A. Completion
loop is unbounded. It owns reboot access outside a prospective driver's mutex.
Any native package must quiesce before shutdown and must not relocate the BAR
away from the HAL's0xC000. This conclusion is from the actual pinned binary,
not merely an assumed ReactOS implementation.

## Validation status

Build-Core001 initially refused parsing (retained source). Corrected invocation
then failed to acquire the global build lease, before any compilation. Empty
artifacts/core001 remains preserved. Core002 later compiled and passed67617 actual
engine cases with ASan/UBSan. model001 was a paused qtest diagnostic: PCI identity,
class and BAR checks passed;0:6.1 readFFFFFFFF. Windows rejected the host transport
with WinError193 before any engine transaction. It is CLOSED/FAIL, never reused.
Core003 WSL transport was never built during contention. The alternative uses the
already-compiled Core002 x86 under Unicorn, hooking only CRT/I/O boundaries.
model002 failed its COFF mapper before any transaction; corrected model003 and
model004 each completed six cases against the actual paused xemu controller.
Conexant model003 returned AV-pack6 and temperatures50/50; Xcalibur model004
correctly returned protocol errors for the absent ADM1032, then succeeded on SMC.
Forbidden EEPROM/read-to-clear requests made no transaction. Both CLOSED/PASS,
private EEPROM unchanged. This is compiled-function/device-model evidence, never
a Windows load/PnP install, ordinary boot or physical result. Source/harness/PE/
firmware/config pins and full qtest transcripts are retained per attempt.

xwnsmb003.c/xwnsmb.inf/xwnsmb-probe.c are an unqualified NT5 prototype, exact full
hardware-ID match, admin/system device ACL, real assigned-port validation and
read-only telemetry. Native001 installed its real binding. Device I/O is serialized with
stop/remove/shutdown, lower IRP completion retains remove ownership, and elevated
power IRPs are queued to passive work before quiescence. Failed power transitions
restore the prior access gate. Full power-policy/lifecycle review and runtime tests
are still required; compiling this draft cannot establish that it is safe to deploy.

Driver001 failed the pool-tag multichar warning under-Werror. Driver002 compiled
the kernel driver but failed the probe's missing winioctl.h; its exact source and
binary are retained. Neither may be installed: that draft validated resources
only after lower START, too late to protect the HAL from PCI relocation.
Candidate003 adds constraints.h to pin the observed NT5 BAR1 requirement group
toC000 before allocation, preserving other groups/order/private tags. It rejects
unrecognized layouts and checks translated resources before forwarding START.
test-constraints.c passed 2,954 actual physical189/malformed-input atomicity cases
under ASan/UBSan. Runtime resource-manager behavior remains open.

Driver003 compiled the constrained kernel, but probe linking failed on unresolved
memset under -nostdlib. The failed source and partial build are retained. Driver004
reuses that exact kernel and builds the corrected probe and explicit narrow
SetupAPI installer. Kernel SHA256:
15dba6948fd9184d09d94a4ab1517c2b86e8497af0e361b41359d1c20fc8057e.
driver004-build.json pins the complete package and sources; driver004-review.json
checks x86/subsystem5.0/imports/nonpaged sections; driver004-exports.json resolves
forwarding and the dynamic newdev.dll lookup. These are static checks, not loading,
PnP, functionality, security enforcement or persistent binding evidence.

prepare-native.py stages only the real package and startup invocation into a fresh
owned child of immutable201, then converts/verifies a standalone source. It does
not edit registry bindings. Native001 is a bounded installation diagnostic with
no cancellation helper; host closure explicitly cannot qualify normal shutdown.
audit-native.py collects actual installer/probe logs, typed device/driver/service
joins, structural/checksummed hives, full allocation, protected files and history.
Native001 is CLOSED: launch accepted at23:39:33UTC, host bound at23:42:33UTC.
SetupAPI selected exact full hardware ID and Telemetry, copied the driver and
reported successful full installation. Typed current-control-set state links
oem3.inf/Telemetry to xwnsmb, demand-start3, ConfigFlags0. Live probe reports
CM_SUCCESS, problem0, DN_STARTED, AV-pack6, temperatures50/50, rejected requests
error87, and successful final SMC recovery. telemetry.json independently validates
all six cases. providers002.json verifies the installed driver and OEM INF match
the package byte-for-byte. No cancellation helper or registry binding edit ran.

The cold audit passes five structural/checksummed/equal-sequence hives, protected
hashes, event/SetupAPI history and full allocation (zero errors/orphans). The only
new warning/error is inherited Ftdisk49. No normal shutdown occurred; this evidence
does not establish persistent cold-boot support or hardware readiness.

Native002 staged cycle001 into a fresh copy of this actual installed state. The
startup runs only telemetry and a guarded normal restart, never installation.
The probe requires correct telemetry, five seconds of genuine installation idle
within30 seconds, and a final idle recheck. Any pending installation causes an
explicit hold without dismissing a dialog. cycle001 build/import review passed.
Its launch was accepted at23:49:22UTC and its host bound closed at23:52:23UTC.
The fresh cycle-00.log (absent from independently scanned source directories)
passes all six cases, CM_SUCCESS/problem0/DN_STARTED and telemetry_valid1. The
typed target binding, prior installer log and prior probe log are unchanged.
New SetupAPI contains no01B4 installation and does identify audio01B0 with
0xe0000228. The global pending query stayed non-idle and logged
restart_blocked_pending_install258; no restart request occurred. This query does
not enumerate every pending device, so01B0 is an observed unresolved device,
not a claim that it is the only outstanding installer.

Native002 cold integrity again passes all protected/installed files, five hives,
history and full allocation with zero errors/orphans. No normal shutdown event;
the sole new warning/error is inherited Ftdisk49. closure.json pins each closed
attempt and refuses ordinary/persistence/hardware promotion. One cold relaunch
shows retained working binding; the required two normal-shutdown cycles remain
blocked until genuine supported setup completion in the other workstreams.

providers001.json pins a read-only extraction from immutable201 standalone seed
d781e58749e7eeb3e2b6b68520a2ed4186eb83d510186b1e52d27e20d0dde904.
NT5 kernel/HAL/provider hashes that have physical189 pins match. PCI.SYS5.0.2195.6933
is extracted emulator-seed provenance, not a fresh physical loaded-module capture.
machine.inf has no01B4/01C1 match; installed audio oem1.inf matches01B1 only.
Original extracted media/binaries remain private and excluded from version control.
Hardware-ready: FALSE. Working binding retained across one cold relaunch: TRUE.
Full persistence/ordinary-shutdown qualification: BLOCKED, not passed.
Inherited Ftdisk49 remains a strict whole-boot failure. 01C1 still requires physical
codec/resource evidence from the coordinator; xemu does not implement that function.

## Primary references

- Xbox SMBus reverse engineering: https://xboxdevwiki.net/SMBus
- xemu controller: https://github.com/xemu-project/xemu/blob/master/hw/xbox/amd_smbus.c
- xemu topology: https://github.com/xemu-project/xemu/blob/master/hw/xbox/xbox_pci.c
- xemu ACI: https://github.com/xemu-project/xemu/blob/master/hw/xbox/mcpx/aci.c
- Linux explicit01C1 modem support: https://github.com/torvalds/linux/blob/master/sound/pci/intel8x0m.c

Owned xemu source read-only HEAD e72e76bd1f12ce45c6c63b4196c6918ea2cc705d.
The model has SMBus0:1.1 and ACI0:6.0, no AC'97 modem0:6.1. Do not substitute
QEMU1B36:0005 or fabricate a null modem merely to clear the physical prompt.

## Processes

All owned emulators, builds, cold readers and waiters are CLOSED, including
14882/36698. No physical session exists. No inter-chat messages were sent.
No main/tag changes. Immutable0.1.0/original0088/physical0101/video0093 preserved.

## Delivery

Implementation and evidence commit: da73019192e8f98bb41a630a539e7ad07d1e4d7e,
pushed successfully to origin/codex/xbox-native-pci. Repository checks passed
for binary/media/credential exclusions and staged whitespace. Native sources
and reports only; original Windows media, firmware, hives, disks and binaries
remain private. No PR, main merge, tag edit or inter-chat message was created.

Several large push attempts stalled and were closed. The remote advertised a
new main commit absent from the local object database. Fetching that reference
without changing the local branch/worktree let Git exclude the already-remote
history: the final pack was105 objects/124.17KiB instead of10663 objects/8.61MiB,
and the PCI branch push succeeded. The earlier transport stall's deeper cause
is not established. No global Git settings or ownership exception were changed;
Git for Windows used a per-command exception for this assigned E: checkout.
