# Interpreting instruction-location controls

Eight20-second cases run sequentially: sleep, arithmetic, memory copy, GDI copy,
then the same four with buffered main-thread snapshots. A separate five-second
sleep supplies marker case0; the workloads use marker cases1..8. No host capture
or input is sent during those intervals. The observer thread has elevated
priority in both conditions and sleeps between observations using a bounded,
deterministic jitter schedule. This is part of the experimental method, not a
production scheduling change.

Main-thread CPU must account for process CPU within100ms. Sleep CPU must stay
below10%; other busy controls must exceed70%. Sampled arithmetic and memory-copy
locations must fall within their separately decoded original assembly ranges in
at least half the observations; sleep locations must show the known ntdll stub
module in at least80%. These are admission checks for gross location attribution,
not estimates of kernel-function CPU costs. GDI observations are retained by
module without requiring a predetermined distribution.

Every snapshot must have a user-mode CS, owned module address, increasing time,
valid index, at most100ms suspension interval and exactly balanced0/1 suspend/
resume counts. Other already-suspended or exited threads are rejected. Unknown
locations are a failure; no unresolved address is relabeled as useful work.
Independent host elapsed agreement is required within250ms per20s interval.
QPC values remain diagnostic only. Read actual review and raw records for results.
