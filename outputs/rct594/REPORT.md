# RCT594: physical save and normal-restart readback passed

The corrected helper passed on the original development Xbox. Immediately after
the Save dialog closed, its first file-open returned2 (not found), then32 (sharing
violation). The first successful complete read finished4080ms after observation
started. Four equal full reads spanned3255ms; total observation took7605ms.
These include file-read/hash/logging overhead and are not isolated save latency.
This supports the timing explanation for the earlier immediate-read failure;
it does not relabel that earlier failed gate as a pass.

The new290247byte XWN593.SV4 survived normal restart with guest/cold SHA1
9887b66f5edb151b63cc313fd2797e05f7416358. Its SHA256 is
fe67dd7567ecd6282b30715a2c0e668a3b9c3baab57b7f7bdce5f1dc69feb77d.
The prior XWN586.SV4 remains byte-identical. Private before/after captures show
the paused park intact; all165600 pixels in the inspected interior comparison
region match. No Load was performed in594.

The dashboard returned at00:57:46UTC after the single accepted00:54:13 launch.
Collection removed the hook first and retained39 files plus504game inventory
entries. RCT exited0 without forced termination; desktop/registry were restored.
EventLog6006 increased by1 and all five system hives plus the user hive passed
audits. Protected720p, ordinary launcher/startup and Welcome preference were
preserved. Ftdisk49 recurred. This is selected-file persistence evidence, not
a whole FATX allocation audit or storage-health clearance.

This attempt uses the exact helper qualified by PC593. It keeps the original
launcher, startup script and720p baseline. A503file game tree, including the
prior physical592 XWN586.SV4, was verified and moved within owned E paths from
xwn586-kit/game to xwn593-kit/game. Only two known mutable retail files were
restored from verified pristine assets. The old save was never overwritten.
The next save target is XWN593.SV4, absent before this attempt.

Stage001 failed on an FTP PASV502 reply after the move and two config restores.
It had verified503 source files and189 destination entries; no helper upload,
startup hook or launch had occurred. Its records remain immutable. Stage002
used fresh connections per file but ran too slowly for its600second verification
budget. Its exact owned child was stopped while still read-only, with no hook
or writes; the nonzero host exit is retained. It was not a console reset.

Stage003 used at most16files per FTP connection, reading each file twice and
checking its expected size/hash. Recognized read-only transport failures get
at most one retry on a fresh connection; data mismatch fails immediately.
Seven batch fault tests and nine recovery-controller cases passed. The actual
stage completed without read failures. No folder/config mutation was replayed.
Only the new helper and startup hook were written by stage003, hook last.

All505 staged entries and12 baseline entries were reverified before the one
SITE request, accepted at2026-10-20T00:54:13.664537Z. The script's inherited
unattended=false field is not a user screen report: no user observation has been
received for594. The result above comes from new records and private captures.
All owned host processes are closed and no test startup hook remains. The console
was at the dashboard at collection. This attempt is CLOSED; never rerun or
recollect it. The next step is a separate watched Load test, then a fixed-scene
graphics API/performance baseline. User availability for Load has been requested.

Keep the failed stage records, the stopped read-only pass and all previous
physical failures. The run cannot qualify reload, FPS, acceleration, other
consoles, sound, fullscreen or general FATX allocation health.
