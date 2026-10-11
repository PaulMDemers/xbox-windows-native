# Rebalance requests reproduce input-port sharing errors

Three fresh NT5 emulator cases associate the extra keyboard/mouse events with
the diagnostic resource-rebalance request. Both allowed and vetoed rebalances
produced one input-error pair; the no-rebalance control produced none. The
SMBus target recovered in every case, and all cold integrity checks passed.
This narrows the investigation but is not an input-driver fix or whole-boot pass.

| Arm | Actual target sequence | Kbdclass 9 | Mouclass 9 | DHCP 1005 |
| --- | --- | ---: | ---: | ---: |
| Skip rebalance | No QUERY_STOP, STOP or CANCEL_STOP | 0 | 0 | 0 |
| Allow rebalance | QUERY_STOP, STOP, START | 1 | 1 | 0 |
| Veto rebalance | QUERY_STOP, CANCEL_STOP; no STOP | 1 | 1 | 0 |

Each arm used the exact same driver, HAL, installer, INF and newly timestamped
helper. The only prepared payload difference was the startup environment's arm
selector. All cases retained property-change, six D3/D0 transitions, the
held-handle CANCEL_REMOVE check and subsequent safe removal/re-enumeration.
No warning, unrelated setup dialog or device was suppressed.

The installed NT5 message providers resolve full event ID C0050009 to a failure
to enable interrupts on the connected port device. The actual packets record
major function 0 (IRP_MJ_CREATE) and FinalStatus C0000043
(STATUS_SHARING_VIOLATION), with the same class-driver unique error values as
stop001. Thus the message does not by itself establish a hardware interrupt
failure. Static inspection of the pinned class drivers finds an
IoGetDeviceObjectPointer path in their enable helpers; this is a candidate for
runtime tracing, not proof of the observed failing call or conflicting owner.

The input errors were generated approximately 2.2 seconds after the allowed
request and 2.3 seconds after the vetoed request, before the later safe-removal
test. In the veto case, they appeared after the SMBus helper had already observed
CANCEL_STOP recovery. The target did not stop in that arm. This supports tracing
the broader PnP/input-port reopening path rather than attributing the errors
solely to the SMBus target's STOP handler. Other device stacks were not traced,
so their exact PnP requests and functional input behavior remain unknown.

The old DHCP 1005 provider text reports an IP-address conflict. It did not recur
in any of these three cases; its original event is retained and remains
unexplained. One case per arm cannot exclude an intermittent failure. A fresh
combined-case reproduction with a capture limited to the owned virtual NIC is
the next useful network check; no network configuration change is justified yet.

The first host timestamp interpretation was wrong and is preserved in
comparison001.json plus review-correction001.json. Raw FILETIME-derived and
event-log epochs agree. Both guest clocks display four hours ahead of the host;
the frozen guest ActiveTimeBias is 240 minutes. Subtracting that bias places
helper marks inside the host launch/closure intervals. Corrected review002.py
uses raw guest epochs directly for relative event timing, retaining the event
log's one-second resolution. It does not qualify the guest's absolute UTC clock.
No guest was rerun to correct the host analysis.

All three protected-file, five-hive, prior-log-history and complete E:/F:
allocation checks passed. E: allocation metadata matched each prepared fixture.
Each final F: scan found 319 directories, 6,726 files, zero allocation errors and
zero orphan clusters. Trace segments were contiguous and below the per-load cap:
13/18/12 records for skip, 13/31/12 for allow and 13/24/12 for veto.

Every case retained Ftdisk 49 and the pending-install restart hold 258, with
helper exit 33. There was no normal restart request, EventLog 6006 or dashboard
return. Each guest closed at its 180-second host bound. Host closure times were
00:09:03, 00:18:48 and 00:25:55 UTC on October 11 (8:09, 8:18 and 8:25 p.m.
Eastern on October 10). Host stop is not shutdown or durability qualification.

Driver SHA256 remains
3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92;
HAL SHA256 remains
234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255.
The helper builds with the pinned RosBE compiler and actual NT5 imports resolve.
All three installed package hashes match. No new kernel code was compiled.

All PCI guests, cold readers and cooperative leases are closed. Used fixtures
must not be relaunched. No physical access, root integration or other-owner
driver changes occurred. Functional SMBus reads, terminal takeover, normal
restart, repeated-boot persistence and physical qualification remain open.
The next input check should trace the actual failing port-open path and owner
in a new bounded emulator case, preserving the existing drivers and errors.

Evidence: [procedure and primary references](PROCEDURE.md),
[corrected comparison](comparison002.json), [message providers](messages001.json),
[original input packets](old-error-packets001.json),
[clock correction](review-correction001.json), [pipeline](pipeline001.json),
[skip audit](skip001/audit.json), [allow audit](allow001/audit.json),
[veto audit](veto001/audit.json).
