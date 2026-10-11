# HID read-sharing rejection proved

Both keyboard and mouse failures reach HIDCLASS's own read-sharing check.
The new System requests ask for read/write access (0x100003) with read/write
sharing (3). Each device already has one CSRSS-owned read open (0x100001) that
allows only write sharing (2). That existing open denies a second reader.

The immediate rejection condition and owner are now demonstrated at the failure
point, extending inputtrace006's post-failure ownership evidence. This does not
establish why System makes the second opens or whether they affect functional
input. No driver, handle or policy change was made.

## Executed condition and ownership

Exact provider bytes match between the immutable source and closed006 runtime.
HIDCLASS SHA256 is
3bc911b579b691a9447428c2b7791938406705c30497803df25db9cf71846697.
providers001.json also pins kbdhid, mouhid and hidusb. Their binaries remain
private. static-review002.json records the installed instructions and derives
the six counter meanings from their tests, increments and decrements; these
are observations of private structure offsets, not invented public field names.

For each failed CREATE, the resident header and relocated site bytes match the
exact provider. The observed sequence is:

1. RVA ABB: open/read/deny-read counters are 1/1/1; write/deny-write/deny-all
   counters are zero. The incoming access includes read and share mask is 3.
2. RVA AD8: the JNE following the extension+0x38 comparison has EFLAGS0x202,
   so ZF is clear and the read-denial branch is taken.
3. RVA AF9 clears the success flag; RVA B03 assigns C0000043.
4. RVA C78 has C0000043 in the completion local; the IRP and class-helper return
   also contain STATUS_SHARING_VIOLATION.

At B03, each HID context list has exactly one existing entry. Its FILE_OBJECT,
device and FsContext match the earlier successful CSRSS open in this same run.
The CSRSS handle table has 285 nonzero entries, matching its reported count.
The corresponding entry resolves directly to that existing file object:

| Input | Owner at rejection | Handle | Granted access | Existing share mask | Object counts |
|---|---|---|---|---|---|
| Keyboard | csrss.exe, PID160 | 0xB8 | 0x100001 | 2, write sharing only | 1 handle / 2 references |
| Mouse | csrss.exe, PID160 | 0xBC | 0x100001 | 2, write sharing only | 1 handle / 2 references |

Raw HID contexts, handle entries, object headers, branch registers and complete
site ordering are retained in veto001/trace.json and reviewed independently by
review-evidence001.py. The earlier CSRSS opens pass the gate before establishing
the deny-read counters. The new requests' share mask does not override the
existing opens' restriction. Neither failed call traverses IoGetDeviceObjectPointer
or IoCheckShareAccess. The generic class event wording does not identify an
interrupt-controller failure in this observed path.

## Validation and closure

One fresh exact copy of the unchanged rebalance002 veto source was launched.
Driver, HAL, INF, installer, helper and startup payload remain identical. The
observer captured eight class calls and both sharing failures, removed every
breakpoint, and resumed the guest without memory/register edits. Debugger pauses
exclude ordinary timing qualification. Static review001 is retained; review002
removes one disabled redundant assertion without changing the interpretation.

Resource-only installation/recovery, six D3/D0 transitions, invalid-only HAL
probes, QUERY_REMOVE/CANCEL_REMOVE and later removal/re-enumeration pass.
The veto records QUERY_STOP1, CANCEL_STOP1, STOP0 and START3. Per-load trace
lengths 13/24/12 are contiguous and below the 64-record limit.

Cold E/F allocation, protected file bytes, five hive formats/checksums/sequences
and event/SetupAPI history pass. F has 319 directories and 6726 files, with no
allocation errors or orphans. One Kbdclass9 and one Mouclass9 retain CREATE /
C0000043; Ftdisk49 remains a strict failure. DHCP1005 did not recur. Prior failed
attempts, the no-rebalance control and the earlier DHCP event remain unchanged.

Pending install258 still holds restart. No Event6006 or dashboard return occurred.
The guest was host-closed at 2026-10-11T03:24:30.395752Z; this is not normal Windows
shutdown. The immutable source remained unchanged. All owned processes, cold
readers and cooperative leases are closed. No physical-console access or
root/other-driver integration occurred.

Next, identify the kernel/PnP caller and purpose of the System reopen and assess
functional input independently before proposing a fix. Do not close CSRSS handles
or disable a valid sharing check as a workaround. Functional input/network,
SMBus transactions, terminal takeover, normal restart, repeated-boot persistence
and physical qualification remain open.
