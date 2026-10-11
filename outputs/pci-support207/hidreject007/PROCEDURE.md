# HID rejection boundary

Continue inputtrace006 with the identical prepared veto source and unchanged
guest payload. Extract HIDCLASS, kbdhid, mouhid and hidusb from that immutable
source and compare each against the closed006 runtime. Keep provider binaries
private and pin their hashes. Use the existing cooperative build and exclusive
xemu leases and preserve the 20 GiB projected C: reserve.

Review the installed HIDCLASS CREATE handler, its sharing predicates, context
list and counter increment/decrement instructions. Static interpretation alone
does not establish which branch executed. Use a fresh fixture and pin resident
module headers, identity/RVA and relocated bytes before interpreting any hit.

Observe HIDCLASS RVAs ABB (sharing gate), AD8 (read-denial JNE), AF9 (rejection
flag clear), B03 (C0000043 assignment) and C78 (completion preparation). Keep the
class entry/return and CREATE dispatch observations from006. At each HID site,
retain IRP/extension identity, requested access/share, six counters and the
existing context list. At B03, inspect CSRSS's handle table with the previously
validated NT5 layouts/lookup and object-pointer rules. Match table counts, raw
entries, FILE_OBJECT/context/device identity and object reference counts.

Capture successful opens as within-run controls. Interpret counters at their
actual program point: a successful open can change counters before completion,
so a hypothetical predicate computed at completion is not that call's result.
Require the actual AD8 flags, subsequent AF9/B03 path, completed IRP/class status
and retained owner before attributing the rejection to read-sharing denial.

The observer has no guest memory/register write command. Breakpoints and single
steps affect timing. Stop after both failures or the 240-second/4096-iteration
bound, remove breakpoints and resume. The runner has a 300-second host bound.
Cold-audit E/F allocation, protected files, five hives and log history after
closure. A host stop is not normal Windows shutdown.

Do not close CSRSS handles, modify HID policy, patch a driver, integrate another
owner's work or access the physical console as part of this diagnostic. The
immediate sharing predicate does not establish the purpose of System's reopen
or prove functional input loss.
