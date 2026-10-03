# Reproduce the validated desktop test

This kit uses Paul's existing Windows host, private WSL build tree and installed xemu firmware assets. It is not a physical-console installer. No additional Windows ISO is needed.

From PowerShell 7.4 or newer, run `Run-Desktop.ps1`. It verifies the current loader ISO and installed fixture hashes, starts the complete UnleashX/Xromwell chain in a private 64 MiB xemu instance, exercises USB input, and captures state, network packets and audio for ten minutes. Use `-Seconds 3600` for an hour. The test uses snapshot storage and removes its disposable disk afterward. Close or wait for other instances of this task before starting another. Run logs are written under the workspace's `work/runs/<RunId>` directory.

The staged Windows startup diagnostic performs thirty 48 kHz stereo playback cycles, a 4 MiB disk comparison, twenty retention checks of an 8 MiB allocation, a Notepad responsiveness check, 120 pings, three Ethernet disable/enable cycles and sixteen further pings. The network is a restricted private xemu backend; these pings target its virtual gateway. Shutdown is not part of this baseline script.

To rebuild, use the ordered source patches and pinned ReactOS commit in `patch-check-0017.json`. The current source tree is `/home/paul/xbox-windows-native/sources/reactos` in WSL Ubuntu. The private RosBE installation is `/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1`. Build entry points include `Invoke-BuildHal.ps1`, `Invoke-BuildAutorun006.ps1`, `Invoke-BuildNvnetNt5.ps1` and `Invoke-BuildAc97Nt5.ps1`; each acquires the shared build lease. The ordinary-target regression uses `Invoke-BuildNormalAudio.ps1` with experimental flags disabled. Existing artifact names are historical checkpoints: make a fresh ISO filename rather than overwriting a validated image.

`make-iso.py --autorun --loader-directory <new-loader-directory> --output <new-iso-path>` packages the loader, HAL and boot video and verifies ISO readback. It includes no Microsoft Windows files. The installed NTFS disk is separate and comes from the supplied Windows media. Fixture builders make private copies, verify inserted file readback, and preserve their inputs.

The retained debugger-gated loader is for diagnosis. The current autorun ISO does not require a debugger to release Windows entry. Source patches and tests are specific to the recorded Windows kernel build; changing Windows binaries requires another import and ABI audit.

For a console, start with the independent [hardware probe](../native-windows-hardware-probe/README.md) and [physical preflight](HARDWARE-PREFLIGHT.md). Do not write these emulator QCOW2 files to the existing Xbox disk.
