# Xbox565 CLOSED; next is a separate gameplay test

The user observed Deluxe's title/menu and Forest Frontiers on native Xbox, then
reported the restart. The one accepted launch is complete; do not launch again
under this attempt ID. The exact temporary Startup hook has been removed first.

Collection001 hit its 1,200-second bound after 499 files; its failure is retained.
Read-only collection002 fetched only 28 missing paths and pins the partial
record. Both supervisors are closed. Registry review005, audit005 and closeout
review passed: graceful game exit, exact game registry restoration, clean hives,
one new normal-shutdown event, unchanged runtime/launcher and no new application
event. Ftdisk49 remains. Only CSS0.DAT and Game.cfg changed in the game package.
Final001 closes this runtime; do not rerun, recollect or parent it. All owned
processes are closed and the Xbox remains at the dashboard. The first offline
audit's missing libhivex path failure is retained; future independent audits need
LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu.

## Next gameplay evidence

Use a fresh attempt ID and bounded runner, retaining the same verified retail
payload, ordinary launcher and 720p configuration. Do not rerun run565.exe:
it intentionally requires a fresh result directory. Its temporary game registry
settings are restored after the test, so the retained RCT.EXE is not by itself
a documented permanent installation workflow.

The useful next check is a longer watched Deluxe session: audible game sound,
menu/input operation, park scrolling and one construction action. Save under a
new unique name, explicitly observe return to the park, and exit gracefully.
Collect the exact save, runner receipt, hive/event deltas and changed game state
after normal Windows Restart. Only then admit a separate launch to reload that
same save and confirm the park state. Save/reload within one process does not
prove persistence across Windows restarts.

Do not silently dismiss dialogs, force-close an unsaved game and count it as a
clean exit, or infer rendering/audio from process status. Set timing and memory
targets from measurements; the current three-minute check supplies neither FPS
nor sustained-play evidence. A later 30-minute session is the roadmap's broader
playability target, not a prerequisite to preserving this narrow success.

The other two editions remain PC-only results. The Sims is untested. Legacy
D3D sample-ladder progress and native NV2A acceleration remain distinct from
RCT compatibility. Boot intermittency and 1080i stay tabled. The old overnight
automation remains paused; this run does not reactivate it.

Keep retail media/assets, saves, hives and screenshots private. Retain all closed
PC controls and physical failures; do not reopen or parent a closed runtime.
