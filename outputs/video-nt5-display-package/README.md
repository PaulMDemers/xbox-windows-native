# Experimental Windows 2000 display installation package

Historical status of the attempts in this directory: full installation succeeds with the project-owned DLL name, but the next
boot fails with0xB4. Restoring the service start type alone does not fix it.
This package is not qualified for deployment. The physical0093 baseline is untouched.

Later investigation identified the boot failure as FATX paging beyond EOF.
The correction and successful ordinary boots of the installed state are in
[fatx-paging-eof](../fatx-paging-eof/README.md). Those results preserve the failed
attempts below and do not establish physical qualification or a shutdown-popup fix.

The current original xwnvideo.inf targets PCI10DE:02A0 and associates the existing XboxVnt5
system-start service with the display device. It uses the NT5 display-class
SoftwareSettings section for InstalledDisplayDrivers=xwnfb and VgaCompatible=0.
It does not install audio support, set video modes, change caching, or add rendering
acceleration. Version0.1.0.97 identifies this experiment, not a released package.

The package sources and one-shot installation tool are original project code.
Owned Windows INF files were inspected locally for NT5 section conventions; they
are not copied into this directory or committed. No Microsoft binary is bundled
here. The ignored test media contains exactly the already-built0096 miniport and
0097 ReactOS display DLL recorded in fixture-001.json. It does not substitute the
same-named Microsoft framebuf.dll or strip the replacement's nonpaged sections.

## Reproduction and boundaries

Build.ps1 uses the existing pinned RosBE compiler under the project build lease.
review.py checks every static import and the dynamically resolved installation
entry point against owned Windows 2000 exports. prepare.py creates a new child
of the immutable pair004 fixture, stages the INF and byte-identical binaries in
C:\xwninf01, and changes only the test startup script. It verifies cold readback
and that the SYSTEM hive was not altered during staging.

The parent retains the two explicitly documented diagnostic FAILEDINSTALL flags
for unsupported audio devices01B0/01B4. This limits the evidence: these are not
ordinary unmodified device settings, and they are not an audio fix. The GPU is
never given FAILEDINSTALL. The physical candidate0093 baseline is untouched.

Run.ps1/supervise.py own one emulator and issue one launch request per unique
case. install.c exclusively creates install.log, calls the NT5 installation API
with flags0, records its result/reboot requirement, and requests a normal restart
only on success. It does not force installation, dismiss dialogs, suppress
failures, or automatically retry. A stalled installer is a bounded failed test.

Cold audit checks logs and event boundaries, installed INF bytes, the GPU's Driver
and Service links, payload hashes and normal restart evidence. A later boot must
exercise graphics again before even emulator promotion. Generic PnP removal,
stop/start, consumer quiescence, hardware behavior and performance remain separate
qualification work. This is not a full FATX allocation audit.

## Contract references

- [Microsoft: UpdateDriverForPlugAndPlayDevices](https://learn.microsoft.com/en-us/windows/win32/api/newdev/nf-newdev-updatedriverforplugandplaydevicesa)
  documents Windows2000 support and the explicit reboot-result parameter.
- [Microsoft: software registry settings](https://learn.microsoft.com/en-us/windows-hardware/drivers/display/adding-software-registry-settings)
  describes device software keys. Modern examples there include newer driver
  models; the legacy SoftwareSettings convention was checked against owned NT5
  installation media rather than copied from a modern WDDM example.

Results are recorded per attempt; a clean installation is not a general cure for
the previously intermittent shutdown popup.

## Attempts

001 reached a desktop with a hardware wizard, welcome window and blank console.
Unpaused framebuffer reads captured the UI. One Alt-F4 and one targeted mouse
click produced no visible response. The owned VM was stopped at00:15:04UTC for
cold inspection, without a normal guest shutdown. No install.log existed in the
cold disk and no new SetupAPI lines persisted. Driver registration remained
absent; strict audit FAIL. Therefore this does not establish that the installation
API was reached or identify the cause of the stall. It is an interrupted,
interactively investigated attempt, not an unattended installation qualification.

002 starts from the unbooted001 package fixture, not its interrupted run disk.
prepare-preload.py appends C:\xwninf01 to the existing DevicePath in SOFTWARE;
all26907 keys and39233 values are compared, allowing only that value change.
SYSTEM remains byte-identical during preparation. The known graphics/restart
runner replaces the installer startup, allowing normal PnP discovery to find
the package before another updater is launched. This follows the documented
[Windows2000 OEM search-path procedure](https://learn.microsoft.com/en-us/troubleshoot/windows-server/setup-upgrade-and-drivers/add-oem-plug-play-drivers).
Actual installation and reboot results must still pass the cold audit.

002 completed all four pixel checks, five timing loops and one normal restart;
payload checks passed and there were no new unexpected errors or popups. However,
the GPU still had no Driver link, so package qualification FAIL. SetupAPI did
find and select Xbox.Install from the authored INF. It rejected server-side
copy-only installation for missing signature information (0xe000022f), then the
client-side installer copied the files but elevated the existing Ignore policy
to Warn because the proposed destination framebuf.dll is a protected system file.
The successful workload does not establish completed PnP installation.

003 uses xwnvideo.inf as the revised source, staged under the same package INF
path for a fresh, unbooted child. Its destination and InstalledDisplayDrivers
token are xwnfb.dll/xwnfb. The0097 DLL bytes are unchanged. No signing policy,
system protection setting or registry hive is altered during this staging step;
the old protected display DLL is not part of the revised CopyFiles list. Original
xboxvnt5.inf is retained to reproduce the failed002 package.

003 installed successfully through the client-side installer under the existing
policy. Cold metadata has ConfigFlags=0, Driver={DisplayClassGUID}\0001,
InfPath=oem2.inf, the expected matching hardware ID and InstalledDisplayDrivers=xwnfb.
The installed INF and xwnfb.dll bytes match the staged package exactly. SetupAPI
records a query-removal veto (type6, CfgMgr32 code23), requiring reboot, followed
by successful full installation. This is not a successful live PnP stop/start.
Graphics and payload checks passed and normal shutdown occurred, but one
rundll32 shutdown popup makes strict audit FAIL. Do not promote this as a popup fix.

004 clones the cold003 installation state, adjusting only the QCOW backing path.
No guest file, hive or trace is reset. The existing one-shot runner advances to
its second workload directory. This investigates booting the installed state;
it does not erase003's strict failure or qualify arbitrary device removal.

004 failed during boot with STOP0xB4 (0,0,0,0x50000), before the second graphics
workload. The unpaused post-bugcheck RAM capture matches that code. Offline
kernel decoding recovers a self-referencing page directory (not captured CPU
CR3) and validates the kernel module-list anchor. VIDEOPRT is loaded, but no
Xbox miniport or display DLL is present in that list. The GPU devnode has the
XboxVnt5 service and no reported PnP problem; that alone does not prove startup.
Cold registration and file hashes remain correct. There was no normal shutdown.

Comparing003's post-install service values reveals Start=3, despite the INF's
StartType=1; before installation it was1. ImagePath is unchanged.005 is a
disposable child of the clean pre-reboot installed state, restoring only that
active-control-set Start value to1. It tests a specific loading-order hypothesis;
it is not a fixed INF or permission to deploy the package. Do not disable Windows
protection or bypass the demand-start/PnP lifetime issue to claim qualification.

005 also reached STOP0xB4 (0,0,0,0x50000), confirmed from the captured kernel's
bugcheck data; the visible framebuffer was a blank blue panel. The decoded loaded
module list again lacks the Xbox miniport/display and includes VIDEOPRT. This
rejects the simple Start=1 remedy. The next experiment should trace the actual
image-load/device-add path, using the pinned entry bytes in next-probe-plan.json,
rather than infer that service metadata guarantees a loaded driver. Preserve the
failed004/005 disks and RAM captures. Neither the package nor0096/0097 is promoted.
