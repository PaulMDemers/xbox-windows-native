# First upload baseline: harness rejected visibility before drawing

candidate001 CLOSED, accepted 2026-10-08T03:03:40.688194UTC and dashboard returned
03:04:59.834029UTC. Preparation68838, runner59864, supervisor47134 and audit49243
closed. No driver/settings/physical changes. Never relaunch or recollect.

Probe127 logged HARNESS_FAILURE index0/stage1, before initialization of the first
sample or counter snapshots. Its visibility predicate demanded SIMPLEREGION and
exact clip bounds0,0,1024,576. The returned rectangle/type were not recorded, so
the exact reason for rejection is unresolved. LastError8 is not reliable evidence
of allocation failure: no last-error contract or clearing at the failing query.
There are no reference images or upload measurements. Strict qualification FALSE.

Clean cold allocation326directories6762files327directoryclusters, zero errors and
orphans; five structural hives, all protected files/helper/startup/config unchanged,
same96MiB1536cluster pagefile, one normal shutdown/dashboard return and zero warning,
error or application events. Verification remains FALSE, not a driver failure.

Next: a fresh kit must record actual clip bounds and use the already established
bounded uncover procedure requiring visibility of the384x256 test area. Arbitrary
clip size is allowed as a measured independent variable, not assumed full-screen.
Preserve this stricter failed attempt. No drawing/pixel/event gate is waived.
