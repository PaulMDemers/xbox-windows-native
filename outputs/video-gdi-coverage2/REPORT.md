# Ordinary probe119: visibility precondition failure localized

Closed without debugger or UI intervention. Normal shutdown1/dashboard. Actual
log: HARNESS_FAILURE0/error8/stage1; GetClipBox type3(COMPLEXREGION), left/top0,0,
right/bottom424,285. The guard requires a simple clip covering384x256. This failed
before any rendering operation. Error8 may be stale and does not establish memory
exhaustion: GetClipBox itself returned a valid region classification.

Strict workload remains false. Cold integrity/events PASS: full allocation
325dirs6761files326directoryclusters, no errors/orphans,5 structural hives,
protected/payloads/startup unchanged, no warning/error/application events.
Same96MiB/1536-cluster pagefile and inherited configuration. No driver change.

Probe120 in video-gdi-coverage3 brings its own window to top and pumps/waits up to
10seconds, as the older verified GDI harness already did. The same simple-region
and full-coverage requirement remains. No dialog is cancelled or gate waived.
Never relaunch/recollect this closed failed case.
