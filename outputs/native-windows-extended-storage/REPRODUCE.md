# Reproduce extended F testing

Use the existing pinned Windows installation, private Xbox firmware, RosBE and
xemu environment. This kit contains no Microsoft installation files or firmware.
Preserve the physical console baseline; every disk preparation script here is
restricted to named private emulator fixtures.

1. Apply `patch-check-0066.json` to a clean upstream ReactOS checkout using
   `tools/apply-series.py`. `--verify-only` checks the complete chain in a temporary
   Git index. Source base and result trees are pinned in that manifest.
2. The current isolated source is WSL `sources/reactos-extended`; `Build.ps1`
   takes the shared build lease and builds ordinary autorun loader/HAL binaries.
   `build.sh` records every CMake option, including partition-6 opt-in and disabled
   read-only/physical checkpoint diagnostics.
3. Run `audit-hal.py`. Build user-mode probes with `Build-Probe.ps1`,
   `Build-WriteProbe.ps1` and `Build-RebootProbe.ps1`. They use the pinned MinGW
   toolchain without a CRT dependency. The write probe permits only two pattern
   generations in the existing 4,097-byte sentinel, flushes and reopens it, and
   requests a normal Windows shutdown/restart.
4. Package with `native-windows-nt5-kernel/make-iso.py --autorun`, passing this
   kit's artifacts as `--loader-directory` and `--hal-directory`, and
   `native-windows-bootvid-framebuffer/artifacts` as `--bootvid-directory`.
   Choose a fresh output name. `package-004.json` records the tested hashes.
5. `prepare-fixture.py` creates a fresh 250 GB image from the preserved dashboard
   and `nt5-fatx-boot-persistence-002` Windows sources. It stages the high-LBA
   sentinel, copies and verifies the Windows tree, changes C's volume mapping to
   F and enables ATAPI LBA48. The corrected shared `bulk_fatx.py` now initializes
   directory tails as ff. `test-fixture-directories.py` covers that behavior.
6. `prepare-write-fixture.py --reboot` adds the bounded restart probe. The actual
   tested historical image was normalized separately by `normalize-fixture.py`;
   its manifest records all files unchanged. Scripts refuse to replace existing
   outputs, so preserve/rename old artifacts before an intentional rebuild.
7. Run `native-windows-nt5-kernel/Invoke-Diagnostic.ps1` with a fresh RunId,
   the generated ISO and HddSource; use `-LaunchXromwell -Autorun -RetainDisk
   -UsbMouse -AllowFramebufferFallback -AllowGuestReboot`, local ports
   FtpPort4596/MonitorPort4594/GdbPort4595, and Seconds180. It starts a private
   emulator, launches Xromwell over dashboard FTP and records runtime state.
   There are no debugger memory/register changes in these successful runs.
8. After cleanup, use `read-result.py --run <id> --write-generation 1` and
   `audit-cold.py --run <id>`. Repeat from that run's retained hdd with expected
   generation 2. The write probe deliberately refuses a third generation.

`-TraceDiskWrites` is optional instrumentation. `audit-write-trace.py` is intended
for runs stopped before a dashboard restart; it does not remove later Xbox OS
writes from its classification. Cold audits convert into a temporary sparse raw
image and delete it afterward; allow at least 2 GiB of host space beyond the run
disk. Do not run a cold audit against an active VM.

Current corrected fixture: `artifacts/windows2000-f-reboot-002.qcow2`.
Current successful cold disks: `work/runs/nt5-extended-f-007/hdd.qcow2` and
`work/runs/nt5-extended-f-008/hdd.qcow2`. Earlier superseded disks were reclaimed
only after preserving SHA256 records and their reports. No physical files were
replaced in this work session.
