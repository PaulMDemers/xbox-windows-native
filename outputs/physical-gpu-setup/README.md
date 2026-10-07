# Physical GPU registration preparation

This is a controlled device-setup step, not an unattended workload or release
qualification. It reuses the exact authored INF from shutdown-device-install
(SHA256 78be6e5e46a1d5019a53648c9197cbba87f7278413bf5187ac27c5cbf59e38ac)
and unchanged video0093 miniport. The installed Microsoft framebuf.dll is referenced,
never packaged or replaced. FATX0101 and normal idle startup stay unchanged.

The earlier emulator first installation succeeded but its shutdown failed. Three
independent subsequent boots passed. Those results justify a controlled setup
experiment, not a claim that the initial setup/shutdown problem is fixed. No
emulator-only null INF, inherited failed-install flag, signing-policy change or
unknown-device suppression is applied to the console.

physical.py prepare preserves current SOFTWARE/SYSTEM, setup/event logs, startup
and miniport privately. edit-software.py appends C:\xwninf102 to DevicePath in an
offline copy, verifying all26,914 keys and39,260 preexisting values: only that
value changes, with no index normalization conversions. Its hivex runtime needs
LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu.

physical.py stage rechecks the entire captured baseline, creates only the new
/F/xwninf102 package folder, writes/readback-verifies software.bak there, and
installs the single-value SOFTWARE change with exact readback. An upload error
attempts immediate restoration. The system hive and installed binaries are not
edited. The stage JSON determines completion; do not repeat a stage blindly.

Before the next Windows launch, obtain the user's keyboard-unplugged state:
the Razer device hangs Xromwell when attached. Reconnect only at the desktop.
This setup boot should stay at the desktop for supported GPU installation.
Unknown-device prompts must be identified; do not silently cancel them or claim
unsupported hardware works. Use a normal user restart after setup and preserve
new logs/hives, actual GPU binding and driver hashes before judging the result.

The physical C scan has independently identified a legitimate508,559,360-byte
shadowc.img. X/Y game-cache cleanup has completed, but no new Windows capacity
sample/events exist yet. The C low-space gate is unresolved: deleting the
softmod image or waiving/silencing the warning is not part of this setup step.
The original0.1.0 archives and all rollback baselines remain preserved.
