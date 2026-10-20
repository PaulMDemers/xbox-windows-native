# PC608: copy admission failed before game execution

The generated batch retained uppercase TRACE606.EXE while the new media contained
TRACE608.EXE. Source generation replaced lowercase trace and other prefixes but
omitted uppercase TRACE. The guest copied the game assets and RUN608.EXE, then
reported the missing file and stopped at its failure guard. VERIFY608.EXE and the
trace executable were not copied. No runner or game launch was attempted.

Build, source inheritance, native NT5 imports and byte-level503-file media review
passed. Those checks did not verify that the batch's tool references matched the
media manifest; their PASS does not establish executable copy semantics.
The failure screenshot and all original source/media hashes remain preserved.
The unsubmitted run-plan records preparation only, with no action receipt.

The operator closed the failed batch and selected Windows Restart. VM exit0 was
2026-10-20 05:10:24UTC, with no host force. Cold audit enumerated6990 files/314
directories and confirmed503 unchanged game assets, the exact copied runner,
absent trace/verifier/copy-success marker, no game logs or temporary game registry,
unchanged OS/seed, five clean hives with raw-value agreement and one new6006.
Raw event timestamps support normal restart. All owned processes exited.
Inherited DRM decode and incomplete allocation-audit coverage remain.

608 is CLOSED FAILED before game execution. Do not reopen, recollect or parent it.
The qualified607 recorder is unchanged. Next609 corrects the uppercase namespace
and adds an independent script-tool contract checking exact source/destination
names, build/media hashes, failure branches and verifier ordering. Reject608's
actual bad script and synthetic mutations before a fresh immutable404 child.

No new game layout, timing, FPS or acceleration result. Xbox untouched, last
dashboard/no hook;596 SOFTWARE cleanup remains cold-only. Protected720p, ordinary
launcher, saves and transfer ZIPs remain unchanged; ZIPs exclude RCT.
