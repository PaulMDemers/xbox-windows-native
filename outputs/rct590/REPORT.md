# Physical RCT590: windowed controls pass; fullscreen transition incomplete

Original development Xbox, protected1280x720 desktop. Current user photo showed
E613.38MB free; conservative decimal budget left546271136bytes after64MiB
allowance. The earlier stale-budget refusal is retained. No reclamation needed
on the console. Reused only502 verified retail assets from closed583 in a new
owned kit, with exact PC589-qualified helper and no PC-only injection sentinel.

One launch accepted22:20:12UTC; dashboard returned22:24:15UTC. The user observed:

> It did everything up to changing to full screen mode which didn’t come up windows just started restarting then

Nine cold-read captures show the title, Forest Frontiers setup, windowed park
and mode menu. Window client640x480 at screen36,55; desktop1280x720. Independent
visual landmark checks show arrow-key and right-button-drag camera movement.
Window-edge attempt left the scene unchanged (0 changed scene ROI pixels).
These windowed results agree with fresh PC589; movement amounts are not claimed
identical. This does not test moving to the physical desktop edge outside the
window and is not proof of an Xbox input-driver defect.

Mode menu offered Window plus640x480/800x600/1024x768 fullscreen. The helper
submitted the640x480 row click, then reported fullscreen_dimensions_failed=1.
Subsequent log still shows client640x480, desktop1280x720 and live game. It sent
WM_CLOSE, received game exit0 without forced termination, restored registry and
desktop state, then requested normal restart. Thus the full controls matrix is
FAILED/INCOMPLETE, not a successful fullscreen run or evidence of a game crash.
No fullscreen capture or mode-change API return code was obtained.

Current framebuffer miniport source advertises one retained firmware mode
(xboxvnt5.c query/set-mode cases). That is consistent with the failed transition,
but is a source hypothesis, not a traced RCT API result. A fresh bounded mode
inventory/API probe should precede any fullscreen fix. Do not change the driver
or weaken the dimension guard based on this result.

Cleanup passed: hook removed first on return, all39 selected files collected,
EventLog6006 delta1, five system hives plus user hive clean, exact game registry
subtree restored, Welcome preference preserved, protected launcher/startup720p
unchanged. Ftdisk49 remains. No whole-FATX allocation or paging-health claim.
Initial host audit import failures from omitted LD_LIBRARY_PATH are retained;
corrected host audits used the same collected bytes, not another console read.
All supervisors/observer closed. Console at dashboard; no owned hook remains.

590 is CLOSED. Never rerun/recollect/parent this runtime. Next: windowed RCT
save/normal-restart/load on a fresh owned attempt, plus separate read-only mode
inventory/API diagnosis. Fixed-scene API/cost measurements follow persistence.
No game FPS, native GPU acceleration, sound or other-console qualification.
