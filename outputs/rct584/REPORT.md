# PC584: complete input and Welcome control

The unchanged582 runner completed on a fresh immutable404 child with an initial
1024x768 desktop. Earlier581/582 remain closed failures: Explorer's Start guidance
covered the first checked game corner at800x600, including582's bounded90second
wait. At1024x768 the same guidance remained visible outside the640x480 client.
No unknown window was dismissed and no exposure/focus check was waived.

All502 installed assets passed the guest copy verifier before launch (10891ms,
error0); bothCD drives were then independently observed empty. Exact early Welcome
and deliberately injected late Welcome each closed with one WM_CLOSE, process
exit0 and disappearance of the matching window. The startup Show preference
remained1. Both registry restoration and the five system-hive checks passed.

All15 captures completed in the intended order. Independent landscape inspection
and scene ROI comparisons found:

| Mode | Window/screen edge | Right arrow | Right-button drag |
|---|---|---|---|
| Window | No camera movement;0 changed ROI pixels | Camera moved;188047 changed | Camera moved;177196 changed |
| Full Screen640x480 | Camera moved;191111 changed | Camera moved;209831 changed | Camera moved;213864 changed |

Counts cover630x390 scene pixels and are not frame rates. The four game-produced
fullscreen images independently matched passive emulator output in the checked
region, including the screenshot-notification area, after each10second settling
period. The game returned to Window mode and the1024x768 desktop was restored.

Runtime ended12:38:17UTC with exit0, no host quit or deadline. Cold audit found
7012files315directories and one new EventLog6006; game exit0, no forced termination,
protected source/media unchanged. Disk SHA256:
`b4b5a7337abe59b5f009bdf501a6a778ea6e77aa11ff875b31d90a13a55e9675`.
The post-exit automatic screenshot FileNotFoundError race is retained with
process_exit0. Preparation002's missing-parent failure is also retained.

This PC runtime is CLOSED: never reopen, recollect or use it as a parent. Evidence:
[final](final001.json), [input](input-review001.json),
[integration](integration-review001.json), [images](capture-review001.json),
[visual inspection](visual-review001.json), [passive agreement](notification-review001.json),
[cleanup](review001.json). Private images and proprietary assets remain private.

Physical583 uses the exact582 helper without the PC injection sentinel. PC584
qualifies that helper's control flow; it does not establish Xbox input/fullscreen,
save persistence, sound, game FPS or native GPU acceleration.
