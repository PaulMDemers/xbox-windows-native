# Working boot files exact; cold baseline observation requested

A read-only capture after457/458 found the exact known720p launcher, FreeLoader,
ROS loader, HAL, boot-video DLL, FreeLoader configuration and normal startup script.
All seven match the earlier415 working-baseline pins. The current XBE's single
section digest is also valid. The4096-byte existing video trace was preserved;
it has no415 comparison pin here and is not attributed to either failed boot.

Only normal `xwnsetup.cmd` and optional desktop metadata remain in Startup.
No graphics test or automatic restart is scheduled. This capture performed no
remote writes, launch, reset, driver replacement or Xbox C access. Selected-file
agreement is not a full FATX allocation audit or evidence about actual CPU/device
state during a failed handoff.

The user has been asked to turn the console fully off, wait about10 seconds,
turn it on with peripherals unchanged, and launch the original File Explorer
path once. If Windows appears, leave it at the desktop. This is a baseline
observation with no test hook, not a D3D retry or proof of a fix. A later success
would not by itself distinguish power-state effects from other launch-state
differences; record the actual transition and subsequent normal restart separately.

Earlier409/410 instrumented allocation/copy observations and414 emulator stops
remain separate. They do not prove this failure's cause. No speculative allocation,
copy-size, direction-flag, video or kernel patch was made.

Evidence: [read-only capture](capture001.json), [byte/digest review](review001.json).
