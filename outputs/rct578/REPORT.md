# PC578: Save Game dialog inspected and cancelled

The bounded helper reached paused Forest Frontiers, opened Save Game, enumerated
the owned controls, cancelled with Escape and returned to the same park region.
The independently decoded before/after images have zero changed pixels in the
630x390 park region. A passive QMP image shows the modal Save Game dialog, the
Saved Games folder and selected Forest Frontiers.SV4 name.

The game-owned dialog class is #32770; the visible filename Edit has ID1148,
Save Button ID1 and Cancel Button ID2. These class/ID observations guide a fresh
test; HWND values are transient. Cross-process GetWindowText returned empty for
the Edit, so a future save helper must independently verify text readback before
submitting the save. No filename was entered and no saved game was created here.

The VM exited0 at10:23:48UTC without host quit, deadline or capture failure.
Cold collection found6475files before and6997after. Seven native BMPs are valid
and nonuniform. Game exit0, desktop and registry restoration, five independently
clean hives and one new EventLog6006 all passed. The first postprocessing review
was accidentally invoked under WSL despite using Windows paths; its failure is
preserved in review-attempt001.json. Running it on the host passed without any
guest relaunch or repeat cold collection.

This PC control is CLOSED. It does not qualify saving/reloading, Xbox behavior,
frame rate or acceleration. The private transport ISO was retained at closure,
then removed by [scoped cleanup](../rct577/transport578-cleanup001.json) after
all502 source assets, the runner and exact ISO hash were verified. The closed
guest disk and evidence remain; they must not be reopened or used as a new
experiment's parent.
