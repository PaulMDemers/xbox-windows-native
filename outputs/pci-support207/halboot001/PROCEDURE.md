# Controlled native HAL boot validation

The existing installed HAL and reconstructed control are different binaries.
Before treating the ownership candidate as a runtime client provider, boot the
rebuilt control and candidate separately, using the same resource-only package,
base fixture and lifecycle workload. Neither fixture uses the physical console
or an audio/video workstream candidate. The audio report still identifies APU01B0
as unsupported; preserve the normal-restart guard and any pending setup hold.

Inputs, all from the preceding reviewed handoff001 build:

| Variant | HAL SHA256 | Expected XwnSmbusReadV1 export |
|---|---|---|
| Installed historical baseline | a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648 | Absent |
| Rebuilt control | 77333f86600d320687baf61a562ab718c7974ef24d3d614211b87bd971890ade | Absent |
| Ownership candidate | 234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255 | Present |

The one new IOCTL resolves the export at PASSIVE_LEVEL using
[MmGetSystemRoutineAddress](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-mmgetsystemroutineaddress).
It has no caller-supplied address/command: the only possible call is addressFF,
commandFF, which the unchanged broker rejects before claiming ownership or doing
I/O. The previously tested 65,536 address/command combinations cover this pair.
Expected candidate reply: NTSTATUS0, INVALID1, status0, polls0, data0. Expected
control reply: export absent, all remaining fields zero. This proves a native
invalid-input ABI path if observed, not functional transactions or terminal
takeover. The normal telemetry IOCTL remains disabled.

The identical helper receives only the expected export flag through its startup
environment. It queries the ABI on every ordinary resource-interface query,
including after device restart, six D3/D0 transitions and re-enumeration. The
candidate launch is gated on control installation, ABI result, complete resource
lifecycle and cold integrity. Each launch uses a private disk, EEPROM, config and
logs, owned ports4784/4786 and a180-second host bound. The lease covers the full
emulator lifetime. No debugger mutations or UI actions are involved.

Preparation001 failed its no-growth condition before any guest launch. The
private partial control001 is closed and must not be launched. The check occurred
after the offline restore wrote private file/directory blocks but before FAT
flush, so it is not a qualified fixture. The immutable seed was never modified.

Attempt002 uses fresh control002/candidate002 fixtures and the unchanged build001
package. Its preparation audits every E: file/directory allocation before and
after the HAL replacement, then checks full F: allocation, protected files and
five hives. After each guest closes, audit E: ownership again and require its
allocation metadata to match the prepared fixture; repeat the existing F:,
protected-file, hive, typed binding and prior-log-history checks. E: is a separate
16KiB-cluster volume; do not apply the old F: analyzer's64KiB geometry to it.
Eleven positive/corruption cases test the new read-only E: audit. Exact build and
attempt-specific source hashes are retained in build001.json/attempt002-inputs.json.

Successful tests remain emulator evidence. A host stop is not normal shutdown,
event6006 is not dashboard return, and an export probe is not SMBus functionality.
Retain inherited Ftdisk49, unsupported setup and untested STOP/cancel paths.
