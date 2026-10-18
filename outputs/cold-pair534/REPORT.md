# Two power-cycled Windows launches: both reached the desktop

On October 18, 2026, both planned launches through the unchanged ordinary
`E:\Applications\XWNEBoot\default.xbe` reached the Windows desktop. Each followed
a separate user-reported dashboard power-off for about ten seconds and power-on.
The user then used Windows Restart, and authenticated dashboard readback completed.
Exactly two launches were issued; no third is planned.

| Run | Launch UTC | Desktop observed | New EventLog 6005 / 6006 | Registry audit | Ftdisk 49 | Popup 26 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 18:49:20 | Yes | 1 / 1 | All five hives clean | 1 | 3 |
| 2 | 18:54:17 | Yes | 1 / 1 | All five hives clean | 1 | 0 |

The popup records in run 1 identify rundll32.exe initialization failing because
its window station was shutting down. No popup observation was reported by the
user. These warnings and Ftdisk 49 remain limitations: desktop and normal-shutdown
evidence passed, but the strict clean-event condition did not. This was not a
whole-volume FATX allocation health audit.

The five registry hives, system event log and video trace changed during each
Windows run. Independent raw-header, hivex and Python checks accepted all five
hives after each return. The ordinary launcher and startup file stayed exact.
The selected ten files before each launch matched the preceding collected state;
there was no host file reset, trace reseed, guest file write or temporary hook.
The protected 720p configuration was checked and preserved. Dashboard C was not
accessed. Six owned capture/launch supervisors closed successfully.

This contrasts with the prior 532/533 sequence: success after power-on, failure
after Windows Restart, then success after that failed return, with unchanged
launcher and selected input files. The new two-success result strengthens the
case for investigating state retained across a warm restart. It does not identify
the responsible component, prove an every-other-boot rule, or qualify reliability.
Power-off/on before launching is a candidate workaround, not an installed fix.

Windows exit remained Restart in both cases. We did not test the Windows Shut
Down menu against Restart. Front-button power-off and the approximate wait were
user reported; standby rails, exact timing and residual hardware state were not
measured. Order and timing remain possible confounders. An unchanged trace alone
cannot prove no Windows execution, as the successful 533 run demonstrated.

The read-only dashboard probe during run 1 shutdown timed out once at 18:51:05;
that result is preserved in dashboard1.json. Later user confirmation and collection
established dashboard return. No launch was retried. Host validation passed nine
admission cases and eighteen malformed-trace cases; these are harness checks,
not hardware proof. The prior 532 harness failure remains in its original record.

Read final001.json, audit1.json, audit2.json and the observer/launch/supervisor
receipts for exact pins and outcomes. Private raw registry and event data remain
outside the public repository. No proprietary payload is included here.

The console ends at UnleashX with no temporary hook and no queued launch. The
scheduled automation remains paused. NEXT.md calls for source and existing-evidence
review of warm-restart handoff before any further bounded diagnostic. D3D, GPU,
game and release qualification are unchanged.
