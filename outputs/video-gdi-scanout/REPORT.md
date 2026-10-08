# Closed failed startup/scanout observer

candidate001 reached the probe entry but failed to read/pin its code (GDB E14).
249 prior pins and dynamic kernel/loader identities were captured, but no rendering
checkpoint or first CreateFile/exit observation was captured. Full breakpoint
teardown and resume succeeded. The guest was then explicitly stopped; this is
neither a completed workload nor normal shutdown. Demand paging is a hypothesis;
a fresh diagnostic retries entry only after allowing the real CPU fault/step.

Cold audit: no workload log/reference files, no new events or normal shutdown,
clean325/6758/326 allocation, no errors/orphans, protected/payload hashes match,
startup unchanged. SYSTEM structural parse fails after forced stop; other4 parse.
No physical access or driver change. Never relaunch/recollect this closed case.
