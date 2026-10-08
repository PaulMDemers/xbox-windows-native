# Complete enumeration evidence with a corrected NT5 count oracle

candidate001 CLOSED. The trace contains36 markers,132 paired calls and302 resident
code pins. Both traversals of each owned complex clip produced identical rectangle
arrays. The60-island case required eight8-rectangle-capacity batches per pass; the
last batch returned four rectangles with FALSE. Seven evidence mutations are
rejected. All breakpoints were removed and the guest resumed normally.

The original frozen verifier incorrectly required cEnumStart's counted return to
equal the enumerated count when bAll=FALSE and cLimit=4096. Actual returns are
0xFFFFFFFF. start-return-review.json pins the owned NT5 branch: with bAll FALSE,
it bypasses the limit/count comparison and returns -1. That behavior is compatible
with valid counted bEnum buffers and was repeated across every captured traversal.
The original trace-verification.json and verification.json remain FALSE. The new
verify-enumeration.py explicitly verifies the pinned branch and actual -1 return,
while retaining pairing,buffers,coverage,pixels,teardown and all cold gates.
enumeration-verification.json and diagnostic-verification.json PASS. This is an
explicit oracle correction,not a waived guest error or an ordinary run.

All18 exact393216-byte cold images match independent host region oracles:
1,769,472 pixels,normal shutdown/dashboard,327 directories6779 files328 directory
clusters,zero allocation errors/orphans,five structural hives and protected hashes,
unchanged pagefile/configuration,zero warning/error/application events. RAM0111
only added diagnostic traversals; it retained the original upload area. It is not
an optimization candidate or physical qualification.

Accepted2026-10-08T03:52:49.272013UTC; returned03:54:52.272449UTC. Preparation76304,
runner62246,tracer61087,supervisor29341,verifier11767,audit37594 CLOSED. The distinct
probe image base avoided the earlier marker collision. Never relaunch/recollect.
The separate RAM0112 implementation starts from RAM0110 and uses no start count.
