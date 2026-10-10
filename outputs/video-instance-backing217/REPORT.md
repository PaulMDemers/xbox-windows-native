# 217: actual stock allocator and CPU backing

Read-only inspection of the owned Complex4627 kernel established its instance
allocation arithmetic and actual CPU page mappings. It did not establish an
NV2A PRAMIN alias or transfer GPU ownership to NT5. No Windows guest, allocator
call, GPU write, context acquisition or copy was launched in these attempts.

kernel004 captured kernel1.0.4627.1 at80010000, ordinal168 RVAe261 and a directly
reread1KiB window. The used184-byte function, version and globals have no capture
gaps; the private636160-byte image container has111 other unmapped pages. Their
zero placeholders are not resident zeros. map005 matched the actual function
and walked currentCR3=f000 through physical PDE/PTE reads, confirming four CPU
aliases across83feb000..83ffffff map to03feb000..03ffffff using4KiB pages.
Both bounded observers resumed the owned CPU and closed without breakpoints.

The function always returns83ff0000 and writes10000 padding bytes. Request
ffffffff takes a query-only branch. Other requests round to4KiB; shrinking frees
the corresponding PFNs using an internal helper and decrements an observed
counter. Neither GPU MMIO nor ownership handoff is present in these184 bytes.
The stock claimed-size global was5000 in both actual snapshots. Its CPU-managed
20KiB window is therefore[03feb000,03ff0000), below64KiB padding. This overlaps
the retained NT5 bootvid indexed buffer[03fb2d00,04000000) by exactly20KiB.
That is an allocation-layout conflict, not an observed live GPU collision.

The pinned pbkit source calls MmClaimGpuInstanceMemory only withffffffff, then
subtracts5000 from the returned pointer. It does not actually request a new
20KiB allocation; its resulting CPU pointer is otherwise unused. Its PRAMIN
object writes start at offset10000. Those source statements do not prove how
physical NV2A maps PRAMIN to UMA memory. The pinned xemu model has separate
RAMIN storage and cannot qualify that physical alias.

The host arithmetic test executes the captured184 bytes under Unicorn, with
three external helper calls modeled explicitly. All99 cases/891 checks pass:
query non-mutation, rounding, exact freed PFNs, counters, output pointer/padding,
preserved registers and stdcall stack cleanup. This is a binary arithmetic test,
not qualification of the stubbed callees, allocator ownership or GPU behavior.

| Unique attempt | Actual result |
| --- | --- |
| dashboard001 | FTP readiness EOFError; no CPU stop or reads. Original failure retained. A subsequent host closure command incorrectly tried to hash an already discarded clone; retained separately. |
| dashboard002 | FTP ready, RSP interrupt timed out before capability handshake; no memory capture or confirmed resume. Runner terminated the owned process. |
| dashboard003 | FTP readiness90-second bound failed; no CPU stop or reads. Stock surface activity is not a dashboard qualification. |
| kernel004 | Loaded kernel capture/function/global/version verification passed; CPU resumed. |
| map005 | Actual CPU alias page walks passed; CPU resumed. |

All five owned sessions are closed and snapshot clones discarded. The retained
216-control source hash remainsf50befc5e27d438af7d8fea0be995eb3c8bcb5ccc5020d70d018569d371d7a8a.
No cold clone integrity, normal guest shutdown, ordinary NT5 qualification or
physical result is claimed. review.json verifies frozen inputs, parent identity,
capture/cleanup records, byte identities, arithmetic checks and layout evidence.
Physical0101/video0093,0088 rollback and immutable0.1.0 are unchanged.
