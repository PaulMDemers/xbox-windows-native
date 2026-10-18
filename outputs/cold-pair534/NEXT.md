# Next: explain the Windows-restart versus power-on difference

534 contains exactly two new power-cycle launches. Do not rerun its ordinals or
recollect closed snapshots. Both were observed at the Windows desktop. Read
REPORT/final001 for cold audits and warning counts. No third run is planned.
Ordinary720p launcher/startup remain unchanged; no temporary hook was installed.
Automation stays PAUSED and the console ends at the dashboard after normal Restart.

Combine this with532/533: cold-start success, Windows-restart-following failure,
failed-return-following success.534 inserts dashboard front power-off about10s/on
after normal Windows Restart and both launches succeed. This supports investigating
state retained through warm restart; small sample, order/timing and unmeasured
state still limit the conclusion. Front power-off is not measured standby-power
removal. We did not compare Windows Shut Down menu behavior against Restart.

Prioritize source/actual-evidence review of warm restart and Xromwell's assumptions
before more boot repetitions. Identify a discriminating observable boundary,
then if needed prepare a bounded read-only state capture matched across a reported
power-on and a Windows normal-restart return. Preserve actual pre-write versus
final contexts and quantify the diagnostic's perturbation. Reconcile prior closed
CPU/context receipts with the predecessor condition, without relaunching them.
Do not guess which CPU, GPU, interrupt, USB or storage state is responsible and
do not install speculative reset/mapping/interrupt patches or borrow firmware state.

Power-off/on before Windows is a candidate workaround supported by this pair,
not a boot fix or general reliability qualification. Preserve Ftdisk49 and the
rundll32 shutdown popup evidence; these are separate from desktop/normal-shutdown
observations. No whole FATX allocation audit occurred. Unchanged trace bytes
alone cannot prove no Windows execution, as533 demonstrated.

After justified boot coverage, matched496 combined scene remains the D3D target.
Earlier490/492/494 physical passes retain their limited scope; no GPU/game/release
promotion. Keep dashboardC offlimits, same shared ownership lease, exact hashes,
bounded requests/cleanup and projected20GiB C/WSL reserve. No hostE allocation,
historical deletion, backing moves or recovery duplication. No next launch queued.
