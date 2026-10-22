# After652 host receipt prototype

Read REPORT.md, FORMAT.md, host001.json, compiled001.json, bridge001.json and source-review002.json.
652 has no physical candidate and no hardware result.651 is closed. Do not
recollect/relaunch651 or convert652 model outcomes into physical qualification.

1. The explicit bridge is host tested against pinned native request/state,
   trace649 and readback651 types. Before integration, validate its actual caller
   point, quiescent RAM ownership and stack/reserved memory use. Keep pre-write
   and post-failure-blanking distinct; the record does not prove its own phase.
2. Design the native transport separately from the report format. Reusing the
   current BootIdeWriteData unchanged is rejected because it ignores the initial
   DRQ wait failure. Do not move IDE/USB/interrupt initialization before display
   setup just to obtain a logger. That would change the experiment's state.
3. Before enabling any native disk write, establish an owned preallocated slot,
   exact live file-to-sector mapping, partition/disk identity, non-overlap with
   metadata or other files, bounds and readback of the complete fresh seed.
   No guessed sector, shared historical file or firmware-state borrowing.
4. Exercise the exact compiled backend in a new owned diskless controller model
   with stuck-busy, no-DRQ, error, timeout, DMA-active, partial transfer, uncertain
   completion and flush failure. The backend must bound each callback without
   relying solely on the disputed timer. Retain every negative outcome.
5. Only after the integration is justified, prepare a fresh uniquely identified
   candidate and owned fixture. A later physical test requires frozen bytes,
   stage readback, one SITE and bounded observation/collection. No launch is
   currently staged or queued. Keep the ordinary720p launcher and startup intact.

If a practical output transport cannot be qualified without changing the state
under test, document that limitation and reconsider the diagnostic strategy;
do not build an unrelated storage subsystem indefinitely or waive its checks.
