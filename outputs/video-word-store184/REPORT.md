# Scalar framebuffer row copier 115

This experiment compares the existing aligned `REP MOVSD` row copy with eight
ordered scalar 32-bit stores and a word tail. It starts from display112 and does
not include the direct-DIB114 experiment, which showed no upload benefit.

The candidate changes only RAM-primary to uncached scanout row copying. Existing
GDI engine calls, rectangle bounds, complex clipping, surface ownership,
allocation, mode selection and cache attributes are preserved. Aligned,
nonoverlapping rows use the scalar sequence; other rows use the original
`memmove`. Destination stores remain 32-bit, and the unused high pixel byte is
copied as before. The eligibility predicate selects a copy implementation within
the existing valid mapped spans; it is not an external-pointer validation API.

The matched builds differ only in `XWN_UC_STORES`. Both contain the same new
read-only counters, acquired under the existing membership semaphore after row
copying. Rendering and copying occur outside that semaphore. The old112
identity, drawing and scanout-comparison interfaces remain unchanged.

The source tree is `bc4fe943a675e87c34b9916fdf23a11703fa5996`, reconstructed with
the pinned RosBE toolchain. Patch SHA256 is
`3d8febf39e3a5cafe42067a0d2b8478f016cfbfc9b24da20ceaebb07b743cf20`.
Control DLL SHA256 is
`feba078e38a187496e2904ca7de54915b57ec25224fc2bfd260bac87297bc188`;
candidate DLL SHA256 is
`ac68dcc2ff6cfd27ed1580ffa17d99ff1a512b86d8cf99f8f54eef63d96a8ba8`.
The exact build commands, tool hashes and provider checks are in
`build-report.json` and `driver-review.json`.

`instruction-review.json` pins the actual resident upload function and proves
the candidate's eight consecutive 32-bit stores, scalar tail, original fallback
and absence of SIMD/FPU instructions. The control retains the existing copy
routine; its actual bytes contain `REP MOVSD`. This is compiled instruction
evidence, not a throughput result.

The original host001 run passed 44,005 checks but did not explicitly balance all
aligned fast-path block and tail cases. Its source and result are retained.
The separate host002 run added Cartesian mode/alignment/length coverage before
any guest launch: 45,641 ASan/UBSan checks and 16,544 independent byte-oracle
cases passed, including explicit 16 fast, 12 block, eight tail and four small
cases, redzones, unaligned fallback, aliasing and pointer-wrap eligibility.
See `host001-coverage-limit.json` and `host-tests002.json`.

The matched ordinary emulator comparison is recorded separately in
`../video-word-runtime185/`. No physical console was accessed. Emulator timing
cannot establish physical CPU or bus throughput; hardware promotion requires a
separate reviewed comparison and rollback protocol.
