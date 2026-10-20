# RCT592: game ran, save survived restart; helper check failed

The user explicitly requested one watched rerun after not watching591. No new
power cycle was reported. This attempt reused the unchanged qualified helper
and game, with fresh baseline records and its own startup entry. Prior591 remains
closed. One SITE was accepted at23:53:52UTC; the dashboard returned at23:57:29.

Windows and RCT ran. Retained captures show paused Forest Frontiers and the Save
Game menu in a640x480 window on the1280x720 desktop. The helper verified an absent
save target, identified the dialog, set/read back the exact filename, submitted
Save once and observed the dialog close. Its immediately following CreateFile
returned error2; it logged input_sequence_submitted=0 and took no post-save image.

After the normal restart, independent cold collection found XWN586.SV4:
290247 bytes, SHA25687f2ddaf852a1ebfc9f8b2c734bbdedfffe83ce8e2a97fb33d0bb41ce7909fd2.
The file was absent before the test. Thus a new save file survived restart.
Whether dialog closure precedes save completion, or another visibility issue is
involved, is not settled. The immediate one-shot read is insufficient for that
distinction. No reload was attempted; the failed helper gate remains failed.

RCT exited normally with code0, with no forced termination. The helper restored
the desktop and game registry and requested restart. EventLog6006 increased by1;
Ftdisk49 recurred. All five system hives and the user hive passed audits. The owned
hook was removed before collection. Protected startup/launcher/720p and Welcome
settings were preserved. All37 collected files and503 game inventory entries are
recorded; unchanged nonselected game payloads were not rehashed after execution.
This is not a full FATX allocation audit. No performance/acceleration claim.

The attempt is closed as partial save-persistence evidence, not a complete
save/load pass. All owned host processes are closed; console was at UnleashX at
collection. Preserve the game/save and all failed evidence. The user screen
report is pending; append it separately when received.
