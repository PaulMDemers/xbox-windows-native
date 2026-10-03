> Superseded after a physical-console hang. Do not run this v1 XBE again. Use [probe v2](../native-windows-hardware-probe-v2/README.md). V1 read PCI 00:00.1, a known Xbox hang address. The earlier emulator validation did not expose it.

# Xbox hardware inventory probe

This separate nxdk application collects the hardware details needed for the next physical Windows boot experiment. It does not boot Windows. It reads kernel version, RAM statistics, GPU/MCPX revision fields, video settings, PIC ELCR and PCI configuration headers on buses 0 and 1. It does not access EEPROM secrets or issue disk-layout, ATA-locking or PCI-configuration changes. nxdk initializes a 640Ã—480 display, and the application writes one text report beside its XBE.

Copy `artifacts/default.xbe` into a new `E:\Apps\XWNProbe` folder and launch it from UnleashX. After it displays completion, reboot to the dashboard and retrieve `E:\Apps\XWNProbe\xwn-hardware.txt`. Preserve the existing Xromwell and dashboard entries. The probe does not identify every motherboard revision or video encoder conclusively; record the console revision and video cable separately.

The application was built with the installed nxdk at commit `58427c078b4ccb0121f359b6b6c536b3b2914976`. `Invoke-Build.ps1` uses the shared console launcher and a build lease, keeps generated objects in the workspace, and copies the XBE/XISO here.

Emulator validation: `hardware-probe-001` boots the XISO and correctly reports that its optical-disc location is not writable. `hardware-probe-003` launches the same XBE from a private UnleashX FATX folder and successfully saves a report. The extracted report records 64 MiB, twelve PCI functions, ELCR `0x1800`, and LPC routing `0x0e065491`. Screenshots and the complete text are in `evidence/`. The physical console has not run this probe yet.

The inventory uses the [nxdk kernel declarations](https://github.com/XboxDev/nxdk/blob/58427c078b4ccb0121f359b6b6c536b3b2914976/lib/xboxkrnl/xboxkrnl.h) and the kernel PCI-slot convention also shown by [Cxbx's HAL implementation](https://github.com/Cxbx-Reloaded/Cxbx-Reloaded/blob/master/src/core/kernel/exports/EmuKrnlHal.cpp). Register values describe the active Xbox firmware environment; Xromwell can change them before Windows starts.

This application's source is offered under the MIT license in `LICENSE`. Third-party nxdk components retain their own licenses.
