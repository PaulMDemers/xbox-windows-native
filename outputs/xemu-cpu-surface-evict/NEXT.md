# Next bounded validation

All build002 native cases are CLOSED; never launch or collect them again.
control001 is prepared NEVER launched; root build001 candidate is unguarded NEVER
launched. Do not use either for future tests. Read REPORT.md, DESIGN.md,
pair-verification.json and closure.json first. No Windows/hardware change occurred.

1. Audit renderer pending-work scheduling against draw_begin/draw_end and primitive
   batching. The candidate can invalidate current bindings while the clear-based
   tests do not exercise queued vertices. Determine a concrete legal workload and
   runtime discriminator before changing code; do not assume an active-primitive
   guard is sufficient or silently discard a pending download.
2. Build a NEW native fixture with an independent pixel oracle for actual draws,
   overlapping surface addresses/pitches and CPU partial writes. Use explicit
   guest fences and report each transition. Preserve unchanged control/candidate
   binaries to isolate behavior unless evidence requires a new build. Pin any new
   shader/pbkit inputs; shared SDK remains unchanged.
3. Exercise explicit owned-emulator reset and continued guest progress with a fresh
   uniquely named case. Distinguish reset from pbkit teardown or dashboard reboot;
   define the retained versus discarded-data contract from actual renderer code.
   Add Z16/swizzled cases where the eviction policy can affect their backing RAM.
4. Only after native correctness coverage, run matched ordinary Windows correctness
   and full cold checks, then the established top/topx128/lower transfer and window
   performance measurements. Verify the stale dashboard Z16 watch actually disappears
   and positions converge without corruption. Sparse trace durations are not a
   performance result; do not promote this candidate on the current pair alone.

Use unique fresh owned fixtures, leases,20GiB guard, frozen inputs and one-shot
launch/collect records. Last C free~21.4GiB; inspect capacity before preparing more
copies. Do not move backing chains. No physical FTP, deployment or tests are part
of the current emulator optimization work.
