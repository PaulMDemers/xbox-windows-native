# Fresh scalar store build208

Both fresh source builds completed. Source tree
`4e335dc7a23b4fc058db597a1dded0c098af3cb1` matches the reviewed118 tree. The
only paired definition difference is XWN_UC_STORES OFF/ON; text bounds and body
clocks are OFF both. Actual NT5 import/provider and compiled instruction review
passes: candidate has eight ordered32-bit stores, control retains REP MOVSD,
fallback remains, and no vector/FPU instruction was introduced into that body.

The exact184 row header retains its independently recorded45,641 ASan/UBSan
checks and16,544 byte-oracle cases. Those historical tests were not rerun or
attributed to a new attempt. No new row implementation or speculative patch.

An initial build lease refusal occurred before source output creation and is
preserved. Build91073 subsequently acquired the lease and closed successfully.
A later host assertion wrongly expected fresh OFF output to be fully byte-identical
to205. Independent inspection finds all code/data/import/resource/relocation
sections identical; the full binary becomes identical after zeroing only both
explicit PE timestamps and checksum. No input binary was edited or normalized
for deployment. That failed host check did not launch a guest or create a result.

Runtime/hardware validation belongs to fresh209 records. No performance,
installation promotion or physical qualification is established by compilation.

Fresh209 runtime and hardware pairs are now CLOSED. Both pass scoped correctness
with actual scalar coverage, but the physical medians show no speed benefit.
Keep the scalar option OFF. See ../video-scalar-runtime209/REPORT.md for raw
timing limits, strict inherited Ft49 failures and verified original-baseline
restoration. No new driver was promoted.
