# PCI010: HID power-policy registration and system-button capability

The fresh emulator trace explains the post-rebalance opens. Windows registers
its power-policy callback for HID interface arrivals. The emulated keyboard and
mouse each answer the initial system-button capability query successfully with
**zero capabilities**, and Windows cleans up both policy entries before
rebalance. Rebalance disables and re-enables their HID interfaces, generating
fresh arrivals and new power-policy opens. Those opens encounter the previously
proved CSRSS read-sharing conflict.

**Decision:** this evidence does not warrant a PCI-driver change, disabling HID
sharing enforcement, or closing CSRSS handles. These two devices had no active
system-button capability to lose. This is a bounded explanation of these events,
not proof that all input, power-button, wake or shutdown behavior is correct.

## Live evidence

[policy-review002.json](policy-review002.json) checks the captured sequence in
[trace.json](veto001/trace.json), independently of the cold checks in
[evidence-review002.json](evidence-review002.json).

* Registration call 1: category 2, flags 0, HID interface GUID
  `4d1e55b2-f16f-11cf-88cb-001111000030`, context/type 0, callback
  `ntoskrnl!PopNotifyPolicyDevice` RVA `DD976`, status 0. The caller is the
  power registration wrapper at RVA `15AD21`. The relevant kernel entry,
  completion and worker sites were matched against the exact loaded image.
* Initial connections 65/66 succeed. The keyboard IRP `FE5EA208` and mouse IRP
  `FE58FBA8` each submit `IOCTL_GET_SYS_BUTTON_CAPS` (`294140`), complete with
  status 0 and Information 4, and leave capability and supported masks at zero.
  Both reach the policy cleanup branch before HID interfaces are disabled.
  No `IOCTL_GET_SYS_BUTTON_EVENT` (`294144`) request is observed.
* Each HID link has successful enable, disable, enable transitions. The
  corresponding class-specific interface's second enable returns `40000000`
  (already enabled). Each HID link produces arrival, removal, arrival
  notifications. The keyboard removal invokes the policy callback twice;
  the mouse removal invokes it once. Those counts are preserved separately.
* The new arrivals precede connections 128/129, both type 0 and both returning
  `C0000043` from the open. The unchanged HID rejection checks again establish
  System access `100003`/share 3 conflicting with the existing CSRSS access
  `100001`/share 2, including contemporaneous handle ownership and the actual
  HIDCLASS denial branch.

The initial synthetic `C000009D` completion schedules the first policy worker;
it is not a failed capability request. The actual requests subsequently succeed.
Names/constants are cross-checked with Microsoft's
[poclass.h](https://raw.githubusercontent.com/microsoft/win32metadata/main/generation/WinSDK/RecompiledIdlHeaders/shared/poclass.h);
the exact NT5 binary and captured execution establish behavior.

[policy-static001.json](policy-static001.json) also decodes the report
descriptors from source matching the built emulator's recorded source pins.
They provide mouse and keyboard application collections, without a Generic
Desktop System Control collection. This supports the observed zero capability
results; it does not establish physical-console SMC behavior.

## Run and integrity

The unchanged PCI/HAL/INF payload ran in one fresh owned fixture, launched
2026-10-11 04:08:04 UTC. Observation ended at its 240-second limit; the runner
closed the guest at 04:13:05 UTC by bounded host stop. Breakpoints were removed
and the guest resumed before closure. No memory/register writes, input
injection, physical access or other workstream integration occurred.

Cold E/F allocation, protected files, five hives and history checks pass.
F contains 319 directories and 6,726 files, with no allocation errors or
orphan clusters. Resource-only installation, HAL probe, lifecycle and
cancel-remove gates pass. Target counts remain QUERY_STOP 1, CANCEL_STOP 1,
STOP 0, START 3; trace segments contain 13/24/12 records. Payload pins remain:

| Payload | SHA-256 |
| --- | --- |
| xwnrsc.sys | `3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92` |
| HAL | `234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255` |
| INF | `d8b50e1f6e49c7a3d1a0aea3a4fee0219351c9be8b7f8121ab02ab47d8c53e83` |

The Kbdclass/Mouclass event 9 pair, Ftdisk 49 and pending-setup result 258
remain. This run does not qualify normal restart or repeated boot. The earlier
reopen009 basic Start-menu and pointer observations remain separate evidence;
no new functional input test is claimed here.

## Capture limitations and retained attempts

The trace reports `capture_deadline`, not its early success marker. One unrelated
wdmaud registration has no observed return during the window. All four relevant
power-policy connections and all class calls completed. This is not a diagnosis
of an audio hang. The reviewer accepts only this explicitly bounded condition.

Four optional HID enable-caller checks failed at a 16-byte window beginning at
RVA `4209`. Static inspection finds a relocation overlapping its leading edge,
which the old pin helper does not handle. Captured return addresses map to
HIDCLASS RVA `4219`, but corrected resident bytes were not obtained: the prepared
post-trace probe was not executed before guest closure. That optional caller-byte
pin remains unqualified. The HID disable caller and kernel API sites passed
their runtime pins; interface names, arguments and results were captured directly.

The first offline policy reviewer incorrectly required notification and callback
counts to match. Its source and [failure record](policy-review-failure001.json)
are retained; revision 002 checks the observed distinct counts. The frozen
preflight observer and all original evidence remain unchanged.

## Next boundary

Close this event attribution without a speculative driver fix. A meaningful
power-button test needs a fresh fixture with an actual System Control capability
and a before/after event-delivery test, or separately scoped physical evidence.
Current evidence cannot substitute for either. Normal restart/setup, Ftdisk,
network/SMBus, terminal and physical qualification remain separate open gates.
All owned guest sessions and resource leases are closed; never relaunch this
used fixture or reuse the closed hardware220 trial.
