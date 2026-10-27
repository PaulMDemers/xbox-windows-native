#723 kernel setup prefix passed

One launch accepted2026-10-27T16:52:53.493790+00:00. User observed GREEN and
automatic return to UnleashX. Seven flushed/readback files collected once,
double-read identical; executable/source pins and unrelated E directory entries
verified. No Windows, startup hook or manual reset. Code723,11 MMIO writes and
4 CRTC writes attempted, first_mismatch=ffffffff.

The prefix uses exactly704's11 common PRAMDAC values and first4 CRTC values,
with diagnostic readback after each write. All matched. CR19=51 ->10 ->51;
680630=3 ->2 ->3; CR1b=85 ->05 ->05. CR14=0/CR17=e3. CR22 stayedfe, never written.
CR33, geometry/timing, encoder and remaining VGA programming were not executed.

Output/SEQ1, CR11, CR19,630 and selectors passed cleanup checks. Flags were
286 ->086 ->286; CR0=8001003b, CR3=f000, CR4=610. CR1b05 intentionally remained
until firmware return: cleanup_ok is NOT full baseline restoration. No85 retry.
No sustained-performance, Windows1.6 or native mode-switch qualification.

This establishes the combined prefix's requested values can read back under
Xbox kernel context. Individual716/718/720/721 tests did not establish that
combination. Passing does not locate708/709's failure: they used a native handoff,
extra writes and later stages. Do not rule out native-context effects or use
this result to skip CR22 verification. No register masks/gate waivers introduced.

Build001 passed.305 actual-COFF modeled probe cases cover baseline guards,
each immediate mismatch, lost writes, cleanup/selector failures and exact write
order.2353 compiled layout/pixel cases passed. Probe/layout nonrelocation bytes
match PE/XBE. Maximum modeled critical path2299 instructions is not a physical
time bound. Kernel file/mode calls can hang; watcher/reset was available.

Read schema001.json for all66 words and audit001.json for the decoded arrays.
No build/test/launch/collection failure in723. Tool title retains CR1b from the
scaffolding; unique723 namespace and recorded prefix fields identify this test.
No owned processes or VM; leases released except retained hardware ticket.
Selected E files/entries audited, not a full FATX or hive audit. No C access.
