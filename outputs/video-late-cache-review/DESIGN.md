# Why this transition does not meet the renderer contract

The shared0106 provider lends a stable pointer to the same reserved physical
framebuffer used by bootvid. Its reference lock accounts for consumers; it is
not taken by every renderer. Inbv ownership can change again for a bugcheck.
The current crash success depends on that address staying mapped and resident.

| Proposed transition state | Normal address | Crash renderer address | Result |
| --- | --- | --- | --- |
| Permanent UC, before acquisition | Valid UC | Valid UC | Current tested state |
| Publish WC while retaining UC | Valid new address | Old UC address | Conflicting cache aliases; reject |
| Unmap UC before WC creation | No valid mapping yet | Saved address now invalid | Renderer contract fails |
| Reserve the same VA, unmap, map WC | Same numeric VA after completion | Nonpresent PTEs during gap | Still fails; eight actual-code replay cases |
| WC allocation fails after unmap | No replacement | Saved address invalid | Attempted UC rollback can also fail or leave a gap |
| Keep an extra UC rescue alias | Valid rescue mapping | Valid UC address | WC publication recreates conflicting aliases |
| Change private PTE/cache globals in place | Unreviewed | Unreviewed | No exported transition contract; not implemented |

Disabling ordinary drawing, checking reference count or raising IRQL does not
make these intermediate states crash safe. A lock held across the transition
cannot be a lock the high-IRQL crash renderer must wait for. A saved pointer
cannot be made safe by republishing a different pointer after it has faulted.
This review does not claim exhaustive NMI, SMP or TLB validation.

The reserved APIs reduce reservation failure, but are neither an atomic cache
conversion nor permission to call the mapper on already populated PTEs. Their
actual NT5 bodies reject that use. Public documentation alone would also have
missed that these exports exist in this particular Windows2000 binary.

Decision: do not implement the proposed fixed-physical UC-to-WC transition.
Do not flip MiWriteCombiningPtes, copy INIT code into a driver, replace PAT
entries globally, or retain mixed-cache aliases to get a favorable benchmark.
Keep0106 unchanged. This is a design rejection, not a relaxed test gate.

A separate physical scanout allocation and crash-time scanout switch could be
another architecture. It would require additional reserved memory, validated
NV2A/encoder register and power-state handling, and a crash-safe switch before
drawing. None of that has been implemented or qualified; it is not a shortcut
for this handoff. The nearer bounded experiment is a RAM drawing surface that
continues to upload through the existing UC mapping without altering scanout.
