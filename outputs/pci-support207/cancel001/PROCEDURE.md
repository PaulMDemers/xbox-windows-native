# Native removal-cancellation test

This is one fresh emulator boot using the already boot-tested HAL candidate
234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255.
The driver remains resource-only and its ordinary telemetry IOCTL is disabled.
The native HAL probe still issues only the fixed invalid FF/FF request.
No physical console, other-owner candidate or root fixture is used.

After installation, device restart and six power transitions, the helper verifies
the exact SMBus instance is a leaf, enables SeLoadDriverPrivilege and opens that
instance's interface. It keeps the handle open while calling the Unicode
CM_Query_And_Remove_SubTree API. No application-level removal notification is
registered, because an early application veto would not test the driver path.

Windows2000 tracks outstanding open handles after query-remove completes.
The required evidence is CR_REMOVE_VETOED23, PNP_VetoOutstandingOpen5, an actual
QUERY_REMOVE(1)/CANCEL_REMOVE(3) trace, and a successful IOCTL on the same held
handle with the start counter unchanged and the query counter incremented once.
After closing the handle, a fresh query must work, followed by successful ordinary
removal and re-enumeration. An unexpected successful removal or a different veto
is a held/failed test, not equivalent evidence.

CM_REMOVE_UI_NOT_OK applies only to reporting this intentional, identified veto;
the veto code/name are saved in the log. No unrelated setup dialog is dismissed.
The normal-restart guard remains unchanged. The run has a180-second host bound,
then independent cold E:/F: allocation, protected-file, five-hive and history checks.
The same E: audit already tested in halboot001 is used byte-for-byte.

STOP and CANCEL_STOP are different IRPs. The documented SetupAPI guidance says
components should use DICS_PROPCHANGE instead of DICS_STOP/START, and the former
has produced removal/recreation in these actual NT5 traces. This cancellation
test does not manufacture or claim a resource-rebalance STOP sequence.

Even a successful result is only first-boot emulator evidence. It does not
establish normal restart, repeated-boot storage safety, functional SMBus reads,
terminal takeover or physical readiness. The separate reported USB second-boot
failure does not become covered by these fresh-fixture cold checks.

Primary API references:

- [Query-remove handling and open handles](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/handling-an-irp-mn-query-remove-device-request)
- [CANCEL_REMOVE handling](https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/irp-mn-cancel-remove-device)
- [SetupAPI state-change guidance](https://learn.microsoft.com/en-us/windows/win32/api/setupapi/ns-setupapi-sp_propchange_params)
