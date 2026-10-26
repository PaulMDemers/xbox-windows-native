# Troubleshooting

| Symptom | First checks |
|---|---|
| Blank screen after choosing Windows | Confirm the current E launcher and record the last screen/LED. Identical launchers have both booted and returned early; a correct path does not rule out the unresolved intermittency. Follow [ordinary boot guidance](installation.md#already-configured-demo); never retry an accepted/uncertain diagnostic launch blindly |
| Xromwell hangs before Windows | Disconnect the keyboard that caused prior boot hangs; keep the mouse connected before boot |
| No mouse after hot-plugging | Input discovery can be blocked by hardware setup; connect the mouse before the next boot |
| Found New Hardware wizards | Record the device name; cancel unsupported devices without disabling them |
| Broken-looking text or moving window contents at 1080i | Return to the matched 720p profile; this was clean in the user comparison |
| Normal text at rest but repaint visible while dragging | Try outline dragging; the desktop is software-rendered |
| Build refuses a changed hash | Inspect the source/tool difference; use explicit development mode for source edits, not an arbitrary compiler substitution |
| Build output directory already exists | Preserve its log and use a fresh attempt directory |
| Resolution selector refuses prerequisites | Stop and identify the installation/package mismatch; do not bypass hashes |
| RCT window-edge scrolling stays still | This matches the tested Window mode; use arrow keys or right-button dragging. Fullscreen needs its own qualified mode path |
| 480p selector copies successfully but Windows returns early | Transfer verification does not qualify boot reliability. Preserve the attempt and restore its exact 720p receipt; separate 480p interaction has passed, but the selector boot cycle remains unqualified |
| UDP diagnostic receives no packets | Preserve receiver readiness, launch receipt and console observation. Firewall setup or a status LED alone does not prove transmission; the latest physical capture did not identify a cause |

If Windows is responsive, save work and restart normally. If the dashboard is
offline, that alone does not prove a crash: Windows may simply still be running.
Record the actual screen and whether a restart was normal or forced.

For a useful issue report include console revision/encoder if known, RAM,
adapter and display, requested/observed mode, exact package or source tree,
last successful configuration, steps, and expected versus actual result.
Photographs and saved screenshots are different evidence; include both when
investigating presentation defects. Remove credentials, product keys, personal
files and console-specific secrets from logs before sharing.

The retained Ftdisk 49 event is a failed strict gate, not silently ignored because
the desktop works. Historical emulator dump-path fixes and the current physical
configuration are separate results. See [development](development.md).
