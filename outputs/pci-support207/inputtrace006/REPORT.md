# Input CREATE path and retained-owner evidence

The bounded trace identifies both failed CREATE paths. A later memory snapshot
proves that CSRSS still held the earlier successful keyboard and mouse opens.
The internal HID rejection condition and its causal relationship to those
handles remain unresolved. No driver or device-policy fix is claimed.

| Input | Observed CREATE chain | Class-helper and IRP result | Retained CSRSS handle |
|---|---|---|---|
| Keyboard | Kbdclass → kbdhid → HidUsb device, CREATE dispatch in HIDCLASS RVA0x88C | C0000043, STATUS_SHARING_VIOLATION | 0xB8, file0xFE4CB608 |
| Mouse | Mouclass → mouhid → HidUsb device, CREATE dispatch in HIDCLASS RVA0x88C | C0000043, STATUS_SHARING_VIOLATION | 0xBC, file0xFE4CBC48 |

The failing calls ran on one System thread/PID8 and used new file objects with
FsContext zero. Earlier successful opens ran in csrss.exe/PID160 and initialized
nonzero HID contexts. Their devices match the later failed CREATE targets:
keyboard0xFE5F0D70 and mouse0xFE5EEDD0. The transient failed file address was reused
between sequential calls; matching addresses do not imply one enduring object.

Eight class-helper calls were captured: four per class, six successful results
and the two sharing failures. The trace verified resident kernel and class site
bytes against exact provider images. It captured151 general kernel opens and
374 IofCallDriver hits during active class helpers, retaining the CREATE steps.
Neither failed class path called IoGetDeviceObjectPointer; no IoCheckShareAccess
breakpoint fired during these observed helpers. The earlier focus on the
object-pointer-open branch was incomplete. No runtime evidence establishes
that stale module caching caused004's missing class-call records.

## Ownership evidence and limits

After removing all breakpoints and resuming, a bounded snapshot found both
earlier file objects with matching type, device and HID context. A private64MiB
memory capture then preserved the state for offline ownership review.
owner-review001.json decodes CSRSS's handle table using the exact NT5 PDB and
the installed kernel's handle-lookup/locking/object-reference instructions.
It finds239 nonzero entries, exactly matching the table's HandleCount. Handles
0xB8/0xBC resolve to the earlier files; each object has HandleCount1 and
PointerCount2, with granted access0x100001. Raw table entries/header bytes and
the instruction evidence are retained.

This proves CSRSS ownership at the post-failure snapshot. It does not prove
continuous ownership at the exact failure instant, sole ownership, or that
these handles caused HIDCLASS to reject the new requests. The next diagnostic
boundary is the exact HIDCLASS/kbdhid/mouhid rejection instruction and its
retained-open state, using pinned provider images and another fresh fixture if
runtime observation is needed. Do not close CSRSS handles or alter device policy
as an inferred fix.

## Workload and cold verification

The immutable source is an exact copy of rebalance002/veto001's prepared source.
Driver, HAL, installer, helper and startup payload are unchanged. SYS SHA256 is
3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92;
HAL SHA256 is234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255.
The host INF now matches canonical d8b50e1f... exactly, and cold installed bytes
match both expected SYS and INF hashes.

The veto produced one QUERY_STOP, one CANCEL_STOP, zero STOP and three total
START records. Per-load trace lengths13/24/12 are contiguous and below64.
Resource-only target recovery, six D3/D0 transitions, invalid-only HAL probes,
QUERY_REMOVE/CANCEL_REMOVE and later removal/re-enumeration completed.
Cold E/F allocation, protected files, five hive formats/checksums/sequences and
event/SetupAPI history passed. F has319 directories/6726 files and no allocation
errors or orphans.

One Kbdclass9 and one Mouclass9 remain, each CREATE/statusC0000043. Ftdisk49 is
still a strict failure. DHCP1005 did not recur; its earlier IP-conflict event
and unchanged rebalance002 control remain preserved. Pending install258/APU01B0
still held restart. There is no Event6006 or dashboard return. Closure at
2026-10-11T01:13:36.822035Z was a bounded host stop, not normal shutdown.

All PCI emulator, observer, cold-reader and lease sessions are closed. The
physical console was not accessed; no root/other-driver integration occurred.
Debugger pauses and post-failure snapshots do not qualify ordinary timing,
functional input/network, SMBus transactions, terminal takeover, normal restart,
repeated-boot persistence or physical readiness.

## Preserved attempts and review

- inputtrace003: historical kernel address produced zero hits; live IDT
  observation found the current base. Closed and cold-audited.
- inputtrace004: correct kernel sites, incomplete class path coverage. Cold
  integrity passed. Original package comparison failed because a text-mode copy
  changed the host INF reference; the guest bytes matched canonical. The failed
  review/pipeline and pinned correction remain unchanged.
- inputtrace005: that original package failure rejected preflight. No fixture
  or guest launch occurred; proposed sources and failed pipeline are preserved.
- inputtrace006: byte-exact host INF, broader class-helper coverage, successful
  bounded trace and post-failure owner review. evidence-review001.json checks
  source/provider/dependency pins, call/IRP status and dispatch identity, retained
  handles, resource traces, cold audits and closure independently.

Raw disks, memory, private providers and binary logs remain private artifacts;
the branch publishes source and compact evidence only.
