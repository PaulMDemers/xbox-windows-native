# Token close belongs to PnP's logoff cleanup

The new resident-pinned runtime observation identifies the higher closing caller:
the owned UMP console control handler at RVA5959 receives argument5, closes its
saved token through kernel32!CloseHandle and clears the saved slot while another
thread is still inside installer process creation. This reproduces and attributes
176's race; it does not identify the separate shutdown popup producer.

Single launch accepted2026-10-09 01:36:13.442350UTC, dashboard01:38:42.163600UTC.
Runner56909/tracer70936/supervisor22465/audit30142 CLOSED.241 events,221 resident
pins,29 creation pairs and82 native pairs; four unreadable hits retained. No
pending returns, complete bounded diagnostic capture, all breakpoints removed and
guest resumed. Same immutable162candidate parent, unchanged112/v4/166runner,
settings/device state. No guest patch or physical FTP/deployment/test.

## Owner lifecycle

All observations are in services.exe PID208, owner EPROCESS4266433216. Saved slot
address1987795812 is UMP base plus RVA15b64. Installer thread4290175008 differs
from closing thread4288417824.

| Events | Tick | Observation |
|---|---:|---|
|42/43|1790|OpenProcessToken call supplies output slot, then returns TRUE; slot0 becomes1896. Exact same thread and12-byte argument pop.|
|196|6657|Installer reads token1896 from the same slot for01B4 creation.|
|202|6659|Console control handler entry, argument5, saved token1896.|
|203|6660|Handler loads token1896.|
|204–207|6660|Other-thread user/kernel NtClose(1896), both return status0.|
|208|6660|Return to UMP RVA599b, CloseHandle BOOL TRUE; slot still1896.|
|209/210|6660|Before/after clear at RVA59ad/59b4:1896 becomes0.|
|222|6675|Installer inner creation returns TRUE.|
|223/224|6675|Its copied handle1896 query fails C0000008 INVALID_HANDLE.|
|233|6678|Outer CreateProcessAsUserW returns FALSE/LastError6.|

The closing wrapper frame is not a guessed chain: exact kernel32 standard
pushEBP/movEBP,ESP prologue and return RVA7ef0 resident pins, EBP=ESP+8 at
NtClose, TEB stack bounds, argument1896 matching the actual close. One frame's
return address resolves to resident-pinned UMP RVA599b. No previous EBP was
walked. `verify-owner.py` independently validates slots, thread/process/order,
paired API statuses, wrapper and higher caller pins and the failing installer.

Cold registration at UMP RVA5ae5/5aea passes this handler to imported
SetConsoleCtrlHandler. Actual runtime argument5 is CTRL_LOGOFF_EVENT, confirmed
in the owned NT5-compatible wincon.h (line101). Later captured controls repeat5
with zero slot and finally6. The callback's private symbol name is not invented;
registration bytes are static evidence, runtime handler/argument/close are actual
observations. No claim of the original physical corruption, token object freeing
or ordinary reproduction frequency.

## Validation and limits

6 identity/residency,5close-scope,5return-scope and6bounded-frame host tests PASS.
Five workload samples/20copy checks/25timed loops/50full-scan RAM/framebuffer RGB
coherence checks PASS. Normal shutdown/dashboard and full cold allocation
322dirs6721files323directory clusters,zero errors/orphans;5hives,protected files
and startup bytes PASS.47 frozen source/input pins and snapshots exact.

StrictFALSE sole exact Ftdisk49/HarddiskVolume6. No popup/application delta here;
174/173/172 popups remain unresolved. The captured token failure without a popup
again distinguishes the two outcomes. No event/settings/service waiver, ordinary
or physical qualification, or driver optimization follows from debugger timing.

The frozen inherited general verifier initially mistook instruction site
owner_acquire_token_return for a paired API return using only its name and refused
with missing entry_index. No output was created. Frozen source remains unchanged;
new offline verify-trace002.py requires explicit entry_index/call fields, verifies
every actual pin/pair, and leaves instruction-site rows separate. Its source,
refusal and output are preserved. This is a host verification schema correction,
not a runtime capture change or relaxed guest gate.

Three closed standalone old runs were copied/readback-hash-verified to E: and
original paths retained through junctions. No active backing-chain parent moved;
manifest outputs/task-storage-offload/manifest-20261009.json.20GiB guard unchanged.
Physical0101/video0093/0088rollback/immutable0.1.0 untouched.

Next178 implements an owned-runner pending-install check before automatic reboot.
It may legitimately refuse restart; such a held test remains incomplete lifecycle
validation. It does not patch UMP or complete unsupported devices. A later genuine
supported installation/completed wizard is needed before clean ordinary reboot;
no automatic dialog cancellation, PnP suppression or popup gate waiver.
