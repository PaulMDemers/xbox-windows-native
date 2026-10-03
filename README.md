# Native Windows on the original Xbox

Experimental native Windows 2000 bootloader/HAL and driver development for a
64 MiB original Xbox. Windows runs directly on the Xbox CPU; xemu is the
host-side test harness.

## Current evidence

- Physical console: Windows kernel entry, processor initialization, HAL base
  setup, RTC calibration, clock setup and partition-hook registration passed.
- Latest physical checkpoint: **XWNR90**, stage 70. Four partition hooks are
  registered and original handlers saved. The probe halts before BIOS memory
  allocation, partition-handler calls, storage drivers or a desktop.
- Private emulator fixtures have reached a Windows 2000 desktop with NTFS,
  USB input, framebuffer, networking and experimental audio. Those results
  do not establish physical hardware compatibility.

See [hardware status](outputs/native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md),
[latest diagnostic](outputs/native-windows-physical-hooks/REPORT.txt), and
[development plan](outputs/native-windows-development-plan.md).

## Source and reproduction

This repository stores our source changes as an ordered patch series against
ReactOS commit `afc0127e8f937ab68503d715d948844973756aa1`, plus build wrappers,
validation tools and reports. The full series and resulting source tree are
in [patch-check-0028.json](outputs/native-windows-physical-hooks/patch-check-0028.json).
Use `python tools/apply-series.py --source PATH --manifest MANIFEST` on a clean
checkout at that exact upstream commit. The script checks the clean baseline,
applies the ordered patches and verifies the resulting Git tree.

Existing build scripts retain Paul's local Windows/WSL paths and pinned
RosBE 2.2.1 compiler. They require local toolchains and user-supplied Windows,
Xbox firmware, dashboard and test media. These are not a self-contained SDK.
Most diagnostic packages also require the preceding preserved binaries.

## Repository contents

Windows binaries, ISOs, registry hives, console firmware/EEPROM, dashboard
archives, disk images, packet captures, raw memory and local scratch data are
excluded. Photos and detailed run dumps remain local; summarized validation
records are tracked. Physical FTP passwords are supplied through the process
environment. Local emulator scripts use the fixture's default credentials.

Preserve the working softmod and dashboard. Hardware probes are manually
launched and photographed; current probes do not automatically return to the
dashboard. Do not write emulator disk images onto the physical Xbox drive.
No native Windows FATX mount or physical Windows boot volume is proven yet.
