# CR06 vertical-total low-byte control792

Fresh kernel-context diagnostic from CLOSED790 source after CLOSED791 native
preservation evidence. Exact pinned704 crtcvtotal524 produces low byte0C.
Capture CR06 EC ->0C ->EC plus eight neighbors; restore CR06 before secondCR07,
CR10 and earlierCR07. No CR16/later timing, encoder, clock or scanout writes.
No complete native mode switch, Windows1.6 desktop or acceleration claim.

Qualification:694 actual compiled-COFF cases (654 inherited,40 new fault/readback/
cleanup cases),2353 compiled allocation cases,10 actual clock-fragment cases,
independent schema mutation review and COFF/PE/XBE linked-byte checks passed.
Failed CR06 undo remains visible in three earlier recovery masks; a corrupted
CR07 neighbor is repaired by its later undo, while corrupted CR10 is observed
by secondCR07 checks before CR10 restores it. Output is inhibited on any mismatch.

Build with pinned nxdk58427c0 under the shared build lease using build.py.
Run model.py,layout_model.py,clock_model.py under the xemu lease; run the three
link reviews and review_prepare.py against fresh receipt paths. Existing attempt
receipts are immutable. restore_model.py only reconstructs exact public text
chunks; it does not reopen a runtime. All executables and connection details
remain private under C:/xwn792.

Physical: unique E/Applications/XWNMode792, exact source/build/stage readback,
one SITE with20second reply bound, intended automatic return after15seconds.
No hook, ordinary launcher/Windows/protected720p edits, or dashboardC access.
Photo/reset workflow: user checks each photo and restarts; authenticate dashboard
before collecting once. Ask about recovery only if the console remains offline.
Manual reset/dashboard return is not normal Windows shutdown.
