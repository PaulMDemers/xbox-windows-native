# Current continuation: reopen009

Read reopen009/REPORT.md, caller-review002.json, input-review001.json and
evidence-review001.json. System reopens are power-policy interface-arrival
connections: IopNotifyDeviceClassChange -> MmDispatchWin32Callout ->
IopPnPHydraCallback -> PopNotifyPolicyDevice -> PopConnectToPolicyDevice(type0)
-> ZwOpenFile. Captured kernel syscall trap, saved EBP, callback stack layout
and exact six open arguments bridge the call chain. Type0 success continuation
selects PopSystemButtonHandler/PopSwitches; it was not executed after the
sharing failure. Upper sites are exact-image reconstruction, not separately
live breakpoint-pinned. Interface arrival GUID and class GUID captured; name
string, registration history and power-button behavior remain unknown.

HID deny-read conflict and contemporaneous CSRSS B8/BC owners reproduced.
After trace cleanup, Ctrl+Esc opened Start, Escape closed only Start, and one
mouse movement moved the pointer. Basic input response observed; full input,
power-button/wake and ordinary timing remain unqualified. Setup dialogs intact.
No sharing bypass, handle closure, guest-policy change or physical access.

Corrected fixture CLOSED2026-10-11T03:53:18.643715Z by bounded host stop; all
owned sessions/leases closed. Cold E/F/protected/five-hive/history and target
resource/HAL/lifecycle/cancel-remove gates pass; QUERY_STOP1/CANCEL_STOP1/STOP0/
START3 and loads13/24/12. Input event pair, Ftdisk49 and pending258 remain.
No normal restart/dashboard return. Preserve failed reopen008 (host dispatch
NameError, zero class calls, cleanup/cold audit pass) and all used fixtures.
Capture-only failures and expired-lease mouse guard are retained in009.

Next if pursuing the event: inspect power-policy interface registration and
reannouncement/system-button capability, with a fresh focused diagnostic.
Do not treat this as evidence for disabling valid sharing enforcement or
closing CSRSS input handles. Network/SMBus, terminal, normal restart/repeated
boot and physical gates remain open; no other-owner integration.

Historical continuation follows unchanged.

# Current continuation: hidreject007

Read hidreject007/REPORT.md, evidence-review001.json and static-review002.json.
Exact HIDCLASS read-sharing denial and contemporaneous owner are proved for
both inputs: new System access100003/share3 meets one CSRSS access100001/share2
open. Extension+38 deny-read count1 leads AD8 JNE (ZF0) to AF9/B03 C0000043;
completion/IRP/class status agree. At B03, live CSRSS PID160 handlesB8/BC map to
the existing HID contexts/files, each handlecount1/pointercount2; table285 entries
matches its count. This advances006's post-failure ownership to rejection-time
causality. No IoGetDeviceObjectPointer/IoCheckShareAccess path, code/handle/policy
change, or physical/other-owner integration. Higher-level reopen purpose and
functional input impact remain unknown. Next trace the kernel/PnP caller and
assess input before proposing a fix; do not disable valid sharing enforcement.

One unchanged veto fixture CLOSED at2026-10-11T03:24:30.395752Z by host stop.
Cold E/F/protected/five-hive/history and target lifecycle/invalid-only HAL probes
pass. QUERY_STOP1/CANCEL_STOP1/STOP0/START3; sequences13/24/12. Input9 pair and
Ftdisk49 remain; DHCP1005 did not recur. Pending setup258 still holds restart.
All owned sessions and leases closed. Control and prior failures preserved.
Functional input/network/SMBus, terminal, normal restart/repeated-boot and
physical qualification remain open.

Historical continuation follows unchanged.

# Current continuation: inputtrace006

Read inputtrace006/REPORT.md, evidence-review001.json and owner-review001.json.
Bounded trace captured Kbdclass/Mouclass forwarding CREATE via kbdhid/mouhid to
HidUsb devices with HIDCLASS dispatchRVA88C; class helper and IRP returned
C0000043 in System context. No class IoGetDeviceObjectPointer or IoCheckShareAccess
path was observed. Post-failure memory proves CSRSS PID160 retained handlesB8/BC
to the prior keyboard/mouse files, each handlecount1/pointercount2. This does not
prove the exact HID rejection condition or causal ownership at failure time.
Next: pin HID provider images and locate that rejection/open-state boundary.
No speculative handle closure, device-policy fix or other-owner integration.

All attempts and leases CLOSED. Preserve003 wrong-base trace,004 incomplete
coverage/host-INF-reference mismatch with pinned correction,005 no-launch
preflight rejection, and006 successful path/owner evidence. Same guest payload;
cold E/F, protected files, five hives and log history pass. Veto QUERY_STOP1,
CANCEL_STOP1, STOP0; lifecycle and invalid-only HAL probes pass. Input9 pair and
Ftdisk49 remain; DHCP1005 did not recur. Pending install258/APU01B0 still holds
normal restart. Functional input/network/SMBus, terminal takeover, repeated-boot,
normal restart and physical gates remain open. No physical access this followup.

Historical continuation follows unchanged.

# Current continuation: rebalance002

Read rebalance002/REPORT.md and comparison002.json. Three fresh same-binary
skip/allow/veto cases are CLOSED. No-rebalance control has no input/DHCP errors;
both rebalance arms reproduce one Kbdclass9/Mouclass9 pair with CREATE and
STATUS_SHARING_VIOLATION. The veto target never stopped. Input errors occur
about2.2/2.3 seconds after request, before later removal. DHCP1005 did not recur;
its earlier IP-conflict report remains unexplained. Target lifecycle and cold
E/F, five-hive and log-history checks pass in all arms. Normal restart remains
held258/APU01B0 and Ftdisk49 remains strict failure. All PCI leases closed.

Corrected comparison002 retains the original clock interpretation mistake:
FILETIME and event epochs agree; both guest clocks are4h ahead of host. Raw
relative guest timing is used; absolute clock accuracy remains unqualified.
Next: bounded read-only trace of the actual input-port open/owner and owned-NIC
packet capture if DHCP reproduces. No speculative device merge or suppression.
Functional SMBus, terminal takeover, normal restart/repeated-boot persistence
and physical gates remain open. Baseline and root fixtures unchanged.

Historical continuation follows; stop001/REPORT.md supplies the intervening
successful native STOP/START and CANCEL_STOP diagnostic before this comparison.

# Next actions

Current continuation: cancel001/REPORT.md. One fresh NT5 emulator boot passed an
actual open-handle QUERY_REMOVE/CANCEL_REMOVE sequence: CR_REMOVE_VETOED23,
OutstandingOpen5, original handle recovered without restart (starts1→1, queries0→1),
then handle closure and successful ordinary removal/re-enumeration. Five native
invalid-only HAL probes and six D3/D0 transitions pass. Cold E/F allocation,
protected files, hives and log history pass. Guest and all leases are CLOSED.
Normal restart still held258 with new SetupAPI audio01B0; strict Ftdisk49 remains.
STOP/CANCEL_STOP, functional reads, terminal takeover, normal restart/persistence
and physical readiness remain open. Do not infer repeated-boot storage safety from
this first-boot result; the separate USB second-boot failure remains outside it.
No physical or root fixture integration, telemetry remains disabled.

Historical pre-cancellation continuation follows.

Current continuation: halboot001/REPORT.md. Rebuilt control and ownership HAL
candidate both booted NT5 in fresh emulator fixtures and passed resource-only
lifecycle. Four native probes found the export absent in control and present in
candidate; the candidate returned INVALID for fixed FF/FF with zero polls/status/
data, including after removal/re-enumeration. Complete E and F allocation, payload,
hive and log-history checks passed. Preparation001's no-growth rejection occurred
before launch; its partial fixture is closed. Fresh002 used audited E growth.
Both runs are CLOSED and held normal restart on pending setup258 (new SetupAPI
names audio01B0). No physical access or functional telemetry. Next gates: supported
pending-setup resolution and ordinary restart/persistence, STOP/cancel coverage,
then coordinated functional-client and terminal validation. Inherited Ftdisk49
remains a strict failure. No PCI build/xemu/cold-reader lease remains active.

Historical pre-native-HAL continuation follows; its unbooted status is superseded.

Current continuation: HAL-LIFECYCLE-REPORT.md and lifecycle004/REPORT.md.
Code10 resource encoding and ANSI removal API compatibility failures are fixed.
The resource-only driver passes live install/start, DICS_PROPCHANGE, six D3/D0
transitions and safe removal/re-enumeration. Normal restart remains held by genuine
pending installation258; new SetupAPI history names audio01B0. No cancellation or
disable was used. All four new guests/cold readers/builds are closed, with scoped
cold integrity passing. No physical access; hardware220 ticket stays closed.
The shared HAL candidate compiles and passes65894 model cases/static review, but
is unbooted; telemetry stays disabled. Next gates are supported pending-setup
completion, a fresh normal restart/persistence test, query-stop/cancel coverage,
and controlled baseline/candidate HAL boot plus coordinated client integration.
Inherited Ftdisk49 remains a strict failure. Do not relaunch closed fixtures.

Historical ownership001 continuation follows; its uninstalled status is superseded.

Current continuation: ownership001/REPORT.md. Physical220 completed and its
restored-baseline ticket closed; commit2d51147 preserves the evidence. The new
offline ownership review found the unconstrained C200 alternative and confirms
HAL takeover as the remaining shared-controller problem. The strengthened policy
passed5432 sanitizer cases and5432 cases in a fresh NT5 guest, with exit0 and
cold file/hive/history/allocation checks. The kernel derivative compiles with
telemetry disabled and remains uninstalled. Build002 and emulator001 are closed;
no console/guest session or lease is active. Next is the coordinated HAL takeover
implementation and genuine PnP/lifecycle tests. Do not reuse the closed hardware220
ticket or enable telemetry before that ownership contract is implemented.

Historical hardware220 preparation follows; its waiting status is superseded.

October10 hardware220 authorization supersedes the physical-access restrictions
in the historical list below. Current continuation is hardware220/REPORT.md:
read-only OS inventory built/reviewed. Emulator001 is closed/held (incomplete
observer, empty exit log, fixture PnP changes); emulator002 closed at05:44:15UTC
after its360-second bound and cold audit reproduced the observer tail at270337.
A reproduced CMD redirection bug is corrected; emulator003 closed without launch.
The coordinator completed root221 and released its leases. Fresh inventory-only
emulator004 closed at05:54:28UTC and cold-audited successfully: inventory/exit0,
protected files, hives, histories and allocation. Its exact typed metadata delta
matches the pinned physical-seed→emulator transition; it is not an unchanged
physical baseline or normal-shutdown qualification. No active PCI process/lease.
Audio then USB must
close restored-baseline tickets before PCI can claim. Never connect to console
FTP before queue.py grants PCI. The functional SMBus prototype remains ineligible
for physical deployment while HAL/video/audio ownership is unresolved.

Historical207 continuation (retain its evidence and failed qualification gates):

1. Native001 installation, six live telemetry cases, typed binding and cold
   integrity passed. Installed driver/OEM INF hashes match. Preserve its closed
   host-stopped result; it is not normal-shutdown/persistence qualification.
2. Native002 passed fresh telemetry from retained binding with unchanged old logs,
   no reinstall and no01B4 install in appended SetupAPI. Cold integrity passed.
   It held restart on genuine pending installation258; appended SetupAPI names
   unresolved audio01B0. This requires other-workstream supported setup completion,
   not a broader PCI INF or cancellation. Retain the closed attempt untouched.
3. Resolve actual runtime failures and complete power/lifecycle/security review.
4. Capture typed selected INF,
   class/Driver/Service linkage and SetupAPI errors. Test telemetry and two consecutive
   ordinary cold boots from persisted state without helper201. Other owners' pending
   devices must remain honestly unresolved; do not broaden/cancel to claim global idle.
5. Document01C1 audio/codec overlap for coordinator inspection. Emulator lacks modem
   function; physical codec/resource presence is not yet known. No physical access
   authorized here. A coordinator-collected read-only resource/codec inventory will
   be required if owned evidence cannot settle it.
6. Before hardware readiness, require all scoped functional/persistence/protected/
   cold-allocation/hive/history gates, preserve strict inheritedFt49 failure, and
   write concrete fresh rollback/preflight/collection protocol. Do not deploy here.

Current processes: none; all native/model/build/cold-audit/wait sessions are closed.
Initial free C:22972096512, E:333771571200 bytes;
recheck projected20GiB guard for every build/fixture. Sources/builds belong to this
E: workstream; original checkout and shared WSL source remain read-only.

Implementation/evidence commit da73019192e8f98bb41a630a539e7ad07d1e4d7e is pushed
to origin/codex/xbox-native-pci. The coordinator can review REPORT/READINESS and
the two closed native attempts. Resume from a fresh attempt after the pending
supported setup and modem evidence blockers have been resolved; do not relaunch
the closed native001/native002 disks.
