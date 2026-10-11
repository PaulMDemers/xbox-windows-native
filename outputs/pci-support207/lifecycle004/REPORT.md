# Genuine resource-only lifecycle passes; normal restart held

The exact SMBus01B4 device installs and starts without Code10 or a reboot
requirement. DICS_PROPCHANGE, three D3/D0 cycles, safe removal and re-enumeration
all complete. The final live interface query again reports profile2, C000,
started1/powered1 and telemetry disabled. Normal restart remains unqualified:
CMP_WaitNoPendingInstallEvents stayed at258 through the30-second idle guard.
No restart request was sent. Probe exit33 retains that hold.

This candidate changes removal to CM_Query_And_Remove_SubTreeW because the actual
NT5 ANSI ExA export is a constant CR_CALL_NOT_IMPLEMENTED stub. The Unicode call
returns CR_SUCCESS; no veto is reported. Interface enumeration then returns259
(no more items). CM_Setup_DevNode(READY) and synchronous re-enumeration succeed,
followed by a fresh valid interface query. Veto names would be retained as UTF-8.

Stage5 of emulator001/resource-trace.json records actual PnP minor dispatches.
It contains two QUERY_REMOVE(1)/REMOVE(2) pairs and three START(0) sequences,
consistent with DICS_PROPCHANGE recreating the device and the later explicit
removal/re-enumeration. No STOP(4) or CANCEL_STOP/CANCEL_REMOVE dispatch is observed;
those individual paths are not claimed tested. Per-extension counters reset on
recreation, so the API result alone was insufficient evidence in earlier trials.
The separate power requests complete six times with status0, target4/gate0 for D3
and target1/gate1 for D0. The final pre-removal power counter is6.

Trace SHA256:8d1bda7d7123044e4077bd38cd2b42049a85db79d26b00e231f900d55861ccf9.
Installed SYS SHA256:4180093077d32a998679b337a5d1749334e81e767f733b6a23d65fae3c9d7314.
Installed OEM-INF SHA256:dc8b0d63947f1341b4a642762214bd63af4d1d0b32cce603159be47ee8033613.
Both package hashes match the reviewed build. Its5,751 resource-policy ASan/UBSan
cases pass, actual NT5 imports resolve and executable sections have no port I/O.

The appended SetupAPI log again names unresolved audio01B0. The precise observed
guard result is pending installation258; that API does not identify a device.
The audio association comes from the corresponding new SetupAPI history. No
setup dialog was dismissed, device disabled, INF broadened or policy bypassed.

The disposable guest launched2026-10-10T20:20:27UTC and closed20:23:27UTC at its
180-second host bound. The runner allowed guest reboot/shutdown, but neither was
requested. No event6006 or dashboard return occurred. Do not relaunch this disk.
The source fixture is unchanged; cold protected-file, five-hive, history and
allocation checks pass (319directories,6726files,320directory clusters,
zero errors/orphans). The full typed binding delta is retained for review;
global configuration equality and two ordinary cold boots remain unqualified.
Inherited Ftdisk49 is still the only new error and remains a whole-boot failure.

All four lifecycle guests and all cold readers are closed; no PCI resource lease
is held. The baseline HAL was retained throughout. The separate handoff001 HAL
candidate is compiled/model/static-tested only, not booted or deployed. No SMBus
transactions or physical-console access occurred. The hardware220 ticket remains
closed. Hardware readiness is false.

Next: supported completion of the pending setup outside this driver's scope;
a fresh ordinary restart/persistence trial; separate query-stop/cancel coverage;
then controlled baseline/candidate HAL boot and broker-client integration. Keep
telemetry disabled until shared ownership and these runtime gates are satisfied.
