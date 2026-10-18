# 544 closed: warm-condition checkpoint reached; boot investigation tabled

The ordinary543 primer reached Windows and returned through normal Windows
Restart (user observation plus EventLog6006 delta1). Without an intervening
power cycle, one fresh544 diagnostic was accepted23:09:16UTC. The user reported
"Red amber with a black screen", matching the pre-PCI checkpoint indication.
After the requested manual reset, the user confirmed dashboard return.

Paired collection completed23:28:45UTC. All ten protected/mutable baseline files
are byte-identical, five hives pass independent checks, and no new Windows events
appeared. Primary, witness and CPU-context receipts decode; no refusal receipt.
Matching-epoch values equal cold542 and the earlier536/540/541 records except
TSC values and preceding marker polls (1146 here,1163 in542). Primary bytes match.
The captured context precedes the final handoff; LED observation is separate
evidence for reaching the later checkpoint. No final PCI/HLT state is claimed.

This did not reproduce the ordinary warm boot failure. Instrumentation changes
I/O, layout and timing, so success does not identify a cause or establish a fix.
No functional PCI, driver, reset or cache patch follows from this comparison.
The original ordinary success/failure/success sequence and cold-start successes
remain valid. Power-cycling or a bounded fresh retry is a practical workaround,
not proof that every other launch succeeds.

Boot investigation is now tabled at the user's request. No further checkpoint
ladder is planned. Return to545 combined D3D scene validation.544 is closed after
one launch; never rerun/recollect this runtime. No hook, owned host process or
queued boot diagnostic remains.720p and ordinary launcher/startup are unchanged.
