# Fresh customized-SP4 assembly405

## Source boundary

Start with the closed clean-media404 OEM installation, whose disk SHA256 is
`ece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796`.
It came from the user-supplied customized SP4 ISO, SHA256
`75ae5e4980e074377d3f0c2ab2e82dff0e3f80400da13c8e2d5a1479d2ccda1f`.
No prepared Xbox Windows tree or machine/user hive is an assembly input.
The private dashboard/firmware fixture is a separate boot dependency; its
Windows partition is not copied. All ten component binaries and the settings
utility come from the fresh release-readiness403 build records.

## Assembly

Extract ordinary files from the PC installation without NTFS metadata, pagefile
or restore/recycle state. Pin every extracted file. Work on private hive copies;
record every requested registry value and prove all other raw values unchanged.
Provision Xbox storage, framebuffer and input boot contracts and the E-to-C
mount identity. Do not invent installed audio/network device instances.
Missing Microsoft input dependencies must come from this same ISO, with exact
cabinet/member provenance and explicit version selection.

Use a new standard 10,000,000,000-byte Xbox image. Preserve factory E root
entries and put Windows on E; the physical console is never contacted.
The writable NBD client is limited to a named owned regular QCOW2 file, an
exact virtual size and aligned bounded operations. Verify through a separate
read-only client, then check every installed file and the full FATX allocation.
Never modify the original PC disk or a completed runtime.

Eight extracted paths cannot be represented by the current FATX writer. Their
exact identities are retained in the assembly manifest. Omitting them is an
explicit failed lossless-transfer gate, not a claim that crypto/DRM/COM+ state
can be discarded safely. The original NTFS disk remains the authoritative copy.

## Runtime phases

Use unique owned emulator runs and local-only monitor/FTP forwards. Capture
each launch once. Ordinary guest logon may use the installation's private
default credentials; values must never enter reports or the source package.
No global driver-signing, device, service or event policy is changed to pass.

The first boot checks persistence and basic offscreen GDI operations, then
requests normal Windows restart. Subsequent children may continue this same
fresh installation after a successful normal shutdown and cold audit. They
are explicitly sequential installation phases, not independent control runs.
Genuine SetupAPI driver installation records exact target IDs, selected service,
return code and devnode status. A later boot checks runtime devices separately.

Every closed run retains logs, full allocation scan, five hive headers and raw
value agreement, event history/deltas, selected installed code hashes and
host shutdown evidence. Audio API completion is not a physical listening test;
offscreen pixel checks are not performance or complete screen validation.
The TCP witness uses a restricted loopback forward, exact independent payloads
and both host/guest results; it is not Internet connectivity qualification.

## Failure handling and storage

Consumed IDs and frozen sources remain immutable. Capacity refusals, compile
failures, loader failures, missing devices and first-boot wizard interactions
remain in their original records. Corrected code gets a new numbered file.
Only verified redundant temporary extraction copies may be removed after the
original disk and assembled file readback are preserved. No backing chain is
moved. The initial RAW conversion underestimated allocation; that reserve
failure remains recorded even though later sparse conversion and split
extraction succeeded. Projected build/runtime guards remain 20 GiB.
