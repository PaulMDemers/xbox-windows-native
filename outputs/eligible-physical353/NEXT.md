353 is CLOSED. The complete fast-path coverage discriminator is solved and
the physical comparison found no material gain. Do not repeat this pair or
promote the candidate as a speed improvement. Preserve the original driver,
all event failures and old349/350 failures.

The next useful discriminator is actual memory behavior: distinguish ordinary
RAM-copy cost from scanout-write cost and establish effective cache attributes
for both actual allocations. Exact351 source allocates ShadowBits with
EngAllocMem(FL_ZERO_MEMORY) and uses the already reviewed local aligned
REP MOVSD memmove. That allocation API and timing alone do not prove actual
PTE/PDE, MTRR/PAT or effective cache type. Do not claim uncached shadow RAM or
an incorrect mapping without runtime evidence.

Review the exact installed mapping/ownership chain and supported CPU/kernel
interfaces before designing a bounded read-only diagnostic. It should pair
actual owner/base/length and page translations with supported cache-state
registers, explicitly reject unsupported/unknown states, and measure separate
owned RAM and current upload work with independent byte checks. Do not change
CR0, MTRRs, PAT, page cache bits, mapping aliases, interrupt state or GPU
ownership to force a result. No speculative write-combining/SIMD patch or
repeat of the earlier unsuccessful scalar upload unroll.

The about24.3 ms upload cost remains a measured target, not proof of its
underlying cause. The RAM-copy body also stayed near16 ms after replacing
EngCopyBits with direct bounded memmove. A new diagnostic needs a concrete
discriminator, meaningful bounds, unique fixtures and the same restoration,
pixel/guard, storage and event gates. Console C stays entirely out of tools.
