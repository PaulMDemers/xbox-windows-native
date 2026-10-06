# Isolate the unfinished audio-device installer

The prior resolved shutdown trace found an active newdev installer for
PCI10DE:01B0, described as Multimedia Audio Controller. SetupAPI had no compatible
driver. This experiment changes only its active-control-set ConfigFlags from
absent to0x40 (FAILEDINSTALL), in a disposable emulator overlay. The control
starts from the exact same immutable0096-miniport/0097-display fixture and leaves
the SYSTEM hive unchanged. All drivers, GDI workload, detached startup and
120-second settling are identical. No physical access or deployment.

This is a configuration intervention to isolate the installer, not an audio
driver, video fix or hardware qualification. The strict popup gate is unchanged.
All hive keys and values are compared before launch, allowing only that one
ConfigFlags addition. Security metadata and timestamps are not part of that
semantic comparison. Raw hashes and owned fixtures are retained. Existing
control failure: video-surface-lifecycle/audit.json. A fresh unchanged control
follows the intervention to avoid treating an intermittent clean run as a fix.

Microsoft documents FAILEDINSTALL as device configuration state set when an
installation fails: [SP_DEVINSTALL_PARAMS](https://learn.microsoft.com/en-us/windows/win32/api/setupapi/ns-setupapi-sp_devinstall_params_w).
The property is writable through [SetupDiSetDeviceRegistryProperty](https://learn.microsoft.com/en-us/windows/win32/api/setupapi/nf-setupapi-setupdisetdeviceregistrypropertya),
available on Windows2000. This offline experiment does not assume the current
documentation or ReactOS implementation proves the owned NT5 runtime behavior.

The audio003 run retained0x40 for01B0 and completed graphics/payload/restart
checks. It still failed the strict gate, now with one shutdown popup. SetupAPI
shows the active installer advanced to01B4. The separate unchanged control003
passed the same strict checks. This is not a passing driver fix.

Based on that observed queue advance, pair004 adds FAILEDINSTALL for exactly
01B0 and01B4, leaving the other devices unchanged. The full hive semantic
comparison permits only those two values. This follow-up tests whether the
remaining interactive installer advances again and whether the popup count
changes; no general PnP suppression, new driver or cache change is involved.
The prior captured control had two popups, so retain the fresh control result
even if it is clean. Counts from these few timed boots are not statistics.

Preparation attempts001 and002 did not launch: absent-value lookup handling
and the shared output-path guard rejected them before guest hive writes. Their
owned children and failure reports remain retained;003/004 are distinct attempts.

## Recorded outcomes

| Case | Selected failed-install flags | Active installer from new SetupAPI records | New popups | Strict audit |
| --- | --- | --- | --- | --- |
| audio003 |01B0 |01B4 |1 |FAIL |
| control003 |None; original SYSTEM bytes |01B0 |0 |PASS |
| pair004 |01B0 and01B4 |02A0 (GPU) |0 |PASS |

All three passed the graphics, payload, UC mapping and normal restart checks.
No debugger was attached. comparison.json retains the checks and limitations.
The unchanged control passed, so these observations do not prove a popup fix.
They do establish that selected installation state changes the active installer.

The last case exposes the GPU installation gap: baseline-pci.json has Service
XboxVnt5 and display ClassGUID for02A0, but no Driver value, and ConfigFlags0x400.
The new SetupAPI records in pair004 show no compatible driver (0xe0000228) for
that exact device. Boot-time service binding is working while a matching PnP
driver installation is incomplete. Do not mark the GPU failed-install to hide
this; next inspect/package a proper Windows2000-compatible display INF and test
the real installer in a new disposable fixture. Miniport stop/remove ownership
still needs validation before hardware promotion. No supported driver was added
or disabled in this experiment.

All owned VMs are closed; last cleanup was2026-10-06T00:01:51UTC. The physical
console remains on the previously verified0093 baseline. No speedup is claimed.
