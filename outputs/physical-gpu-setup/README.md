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

## Single physical launch

After explicit keyboard-unplugged confirmation, trial.py rechecked the staged
state and requested one boot at2026-10-07 01:52:08UTC. UnleashX accepted EXEC.
The console is intended to remain at Windows desktop with normal idle startup.
Actual device setup and subsequent normal-restart collection are pending;
launch acceptance does not establish that Windows or GPU installation succeeded.

## First collection and authorized second launch

User rebooted after difficulty selecting the driver and explicitly requested
relaunch. Collection shows successful GPU installation, reboot required by
query-removal veto, ConfigFlags0/class0001/XboxVnt5/oem2.inf and Start3. The
installed OEM INF exactly matches the staged file; driver hashes are unchanged.
Both SYSTEM and SOFTWARE traverse structurally. Reboot method remains unknown.

A new SetupAPI span contains92 non-ASCII bytes. Repeated readbacks match and the
old log is an exact prefix. Preserve this anomaly as unresolved; it is not a
clean setup qualification. The generic prompts were01B4 followed by01C1; logs
then advance to USBffff:ffff after GPU completion.

second-boot.py requested one separately recorded boot at02:09:25UTC on7October,
after verifying collected state and rollback. UnleashX accepted it. No file
changes or automatic restart were made. Collect with second-boot.py collect once
after user restart; do not repeat either launch or infer desktop success.

## Second boot collected and cold-audited

The user reported no repeated VGA wizard and later completed the requested
normal Windows restart. EventLog confirms one6005/6006 pair. SetupAPI has no
GPU reinstall, preserves the entire first log, and appends3224 ASCII-only bytes;
SYSTEM retains exact GPU class0001/XboxVnt5/oem2.inf/ConfigFlags0 and Start3.
There are no new Application Popup or application-log events. Srv2013 now appears
only for WindowsF (raw Xbox C containing the softmod shadow image); the previous
G/H cache warnings are absent. Strict event qualification still fails.

The unique read-only postboot scan returned and was collected once:6075
directories,122327 files,6080 directory clusters, no orphans or allocation errors.
All3439 manifest binary hashes match and all nine registry hives pass structural,
sequence and checksum validation. Final dashboard reads reconfirm installed
baseline, normal startup, exact GPU OEM INF, preserved SOFTWARE backup and
unchanged collected SYSTEM/SOFTWARE/SetupAPI. All owned processes are closed.

GPU configuration is verified for this user-assisted boot. Overall strict
qualification is false: remaining device prompts, legitimate raw-C capacity
warning and the first boot's malformed log span remain unresolved. First boot
has no6006 record; the optional question about its reboot method is pending.
No release/recovery capture or further Windows launch was performed. See002/
qualification.json, final-state.json and NEXT.md.
