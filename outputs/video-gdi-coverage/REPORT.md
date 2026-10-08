# Real GDI coverage: incomplete ordinary attempt

candidate001 is CLOSED and unqualified. Desktop observation showed no probe
window and no requested restart. The run was explicitly stopped early to inspect
its cold state; early-stop.json retains the reason and snapshot hash. No debugger
was attached. Monitor screendump is unsupported; a read-only framebuffer capture
was used for this observation. No workload or shutdown success is inferred.

Cold audit found no result.log or26 reference files, no new events and zero normal
shutdown events. Allocation is consistent325 directories/6758 files/326 directory
clusters, no errors/orphans. Protected and payload hashes match, startup unchanged.
Four hives parse; SYSTEM fails structural parsing with Bad address after the forced
stop. Configuration and96MiB/1536-cluster pagefile layout remain as prepared.
The failed child is preserved and will not be reused or recollected.

Probe source/API imports were reviewed and compiled under unchanged warning gates.
RAM0109 is unchanged. The initial indentation compiler failure is retained.
A fresh separate video-gdi-scanout diagnostic adds actual probe entry, first file
create/paired return and exit observations to determine why the test did not
produce results. This report does not identify a display-driver defect.
