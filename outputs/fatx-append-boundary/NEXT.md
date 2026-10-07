# Next reproduction stage

Keep the first physical malformed log, both GPU installation records and their
cold audits. Ordinary serial append PASS does not close that investigation.

1. Finish the independent sibling002 run and cold audit before expanding the
   workload. Both children must use the same immutable pre-run parent, unchanged
   0101/video0093 and exact helper; neither is based on the other's output disk.
2. Add a separately identified append-sequence probe closer to a text log: many
   small appends through the recorded offset, close/reopen, and normal shutdown.
   Compare explicit flush after each append versus flush at the end. Preserve
   the current 96-case helper and reports unchanged; do not relabel these results.
   A write-through open plus later explicit flush proves these final bytes only,
   not that the driver independently honored write-through durability semantics.
3. Reconstruct a separate first-GPU-install emulator scenario from an actual
   pre-install fixture, retaining its complete provenance and differences from
   physical hardware. Use the exact reviewed INF and 0101/video0093. Diff setup
   state before changing anything; do not transplant physical hives or simply
   delete a binding and call that a clean first install. Keep the settled-boot
   control and all installer/pending-removal/event records.
4. If corruption reproduces, preserve first failure before adding diagnostics.
   Capture the caller bytes, completed write offset/count and cold destination
   separately. Debugger observations are exploratory and require a subsequent
   unmodified reproduction. No driver patch is justified solely by a sector
   boundary or a negative ordinary test.

Physical work remains separate: explicit handling of remaining device prompts,
legitimate raw-C shadow-partition capacity integration, then unattended soak.
Neither historical warning gates nor the original malformed log are waived.
