# Native Windows 2000 device workstreams

The user requested separate chats for the remaining devices while video work
continues in the original chat. Audio, PCI support and USB/gamepad support each
have an independent checkout and branch. This is development authorization; the
coordinator serializes physical deployments to preserve a working console.

## Shared starting point

Source/evidence baseline: private repository
https://github.com/PaulMDemers/xbox-windows-native.git at 47fe46f. Preserve immutable
0.1.0, original 0088 rollback, physical 0101/video0093, all failed cases and exact
binary/source/fixture provenance. Temporary text 118 physical trials are closed;
original display/SYSTEM and normal startup were restored. Xbox was at UnleashX.

Canonical evidence/artifact workspace (READ ONLY for device chats):
C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility.
Read outputs/engineering-notes/CONTINUATION.md, device-durability189/REPORT.md,
device-observation188, setup-wizard-automation201/REPORT.md and
video-text-oracle206/REPORT.md. Historical 189 actual SetupAPI observations name
audio 01B0, PCI 01B4/01C1 and USB FFFF:FFFF with no-compatible-driver 0xe0000228.
These are leads, not proof of function or a correct compatible-driver match;
derive complete instance/hardware/compatible IDs from pinned preserved evidence.
Do not assume that the USB prompt is a correctly identified gamepad.

Known wizards currently recur on each boot. Helper 201 cancels exactly the known
prompts, then observes genuine installation idle; it does not install drivers,
persist bindings or disable devices. It enables unattended benchmarks only.
Each owner must prove correct persistent bindings, working device behavior and
subsequent ordinary boots without cancelling that owner's device prompt. If an
unrelated known prompt must be handled for a separate benchmark, record its exact
identity/actions and keep that result scoped. Final integrated prompt-free success
requires ordinary boots without the cancellation helper or any recurring wizard.
An honest unresolved device is preferable to a dummy driver that merely hides it.

Physical ping was user-observed working; keyboard/mouse and applications worked.
Preserve network, storage, display and USB input. Sole inherited Ftdisk49 before
measurement remains a strict whole-boot failure; narrow display passes do not
waive it. Historical emulator null/unsupported bindings must not be imported to
the physical console or counted as functional device support.

## Ownership

- Audio: E:/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo,
  branch codex/xbox-native-audio. Own genuinely identified audio functions,
  playback driver/INF and tests. Inspect historical native-windows-nt5-kernel
  audio builders/capture analysis before deciding what is reusable.
- PCI: E:/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo,
  branch codex/xbox-native-pci. Inventory actual PCI/bus bindings and identify the
  two unknown prompts. Own non-audio/non-USB functions; document classification
  and overlap before editing packages belonging to the other owners.
- USB: E:/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/usb/repo,
  branch codex/xbox-native-usb. Identify USBFFFF:FFFF, controller/hub/child topology
  and descriptors, distinguish an enumeration defect from an unsupported gamepad,
  preserve keyboard/mouse and investigate real gamepad/HID support.

Work only in the assigned checkout and private uniquely named build/runtime
directories. Shared toolchains and original evidence are read-only. Do not edit
the coordinator's source, continuation, guest images or shared WSL source tree.
Do not merge/push main, modify tags, or change other workstream branches. Reviewed
source/reports may be committed and pushed to the assigned private branch.
Retain binary/media/credential exclusions and repository checks.

## Execution and console coordination

Apply C:/Users/Paul/.codex/skills/xbox-native-bringup/SKILL.md and its relevant
references. Native NT5/RosBE work is not an nxdk application. Use pinned compiler,
loaded binaries and actual imports rather than an assumed modern Windows API.
Research uncertain hardware using primary sources; retain licensing/provenance.

Global cooperative leases are mandatory:
C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1
supports build, xemu and xemu-ui. Use exclusive xemu for cold qualification or
performance work; never operate another chat's instance. Resource contention means
wait/back off and perform independent source work, not bypass the lease. Each
guest needs an owned fresh disk, EEPROM, ports, config, output guards and namespace.
Use separate WSL source/build directories per owner, not the coordinator's tree.
Preserve the 20GiB C: projected build guard. E: has ample space for new private
outputs; do not relocate an existing backing chain. Immutable originals may be
read, copied to a fresh owned fixture and verified, never edited in place.

Initial development is emulator-only. Do not FTP, deploy, launch or test the
physical Xbox from these chats. Prepare a concrete reviewed hardware package,
fresh rollback/preflight, expected result, collection protocol and rollback, then
record readiness for the coordinator to deploy in sequence. The original video
chat owns all physical testing; existing authorization permits it to act without
asking the user again. Keyboard is always unplugged through Xromwell. Credentials
are not in this document; never request/store them just to perform emulator work.

No event suppression, dump/service disabling, fabricated completion, synthetic
null binding or blanket driver matching to achieve PASS. A legitimately supported
device binding/configuration change must be justified by actual device evidence,
isolated and validated across cold boots. Retain every failure and distinguish
host tests, debugger observations, ordinary emulator results, physical results
and user observations. Preserve installation/event history, normal shutdown,
independent cold allocation, structural hives and protected hashes as appropriate.

Each chat should maintain its own REPORT.md/NEXT.md with exact artifacts, attempt
IDs, conclusions, unresolved questions, branch commits and owned running sessions.
Do not send messages to other chats without direct human authorization. The
coordinator can inspect chat status and branch reports, then integrate reviewed
changes. Keep working autonomously on implementation and meaningful tests until
a hardware-ready milestone or a concrete external/manual blocker is reached.
