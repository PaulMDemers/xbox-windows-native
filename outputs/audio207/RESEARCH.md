# Hardware and NT5 contract

`inventory001.json` pins complete physical instance, hardware and compatible IDs
from closed189, plus actual provider files and existing audio service state from
the preserved emulator fixture. It is read-only evidence, not a new console probe.

The pinned xemu PCI definitions map `01B0` to MCPX APU and `01B1` to MCPX ACI.
The ACI model uses ordinary AC97 implementation beneath its MMIO BAR2 and omits
the I/O BARs. Its codec behavior therefore cannot establish behavior of the
physical Wolfson codec. The APU is a separate voice/DSP device and is not required
by the direct PCM ACI approach. Its unresolved wizard must remain visible as an
unsupported function; no ACI INF may claim 01B0 just to remove that wizard.

Pinned primary sources and SHA256 values are in `research-pins.json`:

- [nxdk audio](https://github.com/XboxDev/nxdk/blob/f2e0e76e3989a4727f981c68608036fcb0a4aff9/lib/hal/audio.c): MIT;
  direct PCM and separate S/PDIF rings; fixed codec differs from PC assumptions.
  Reference only; its unbounded reset waits are not suitable for the NT5 driver.
- [xemu ACI](https://github.com/xemu-project/xemu/blob/704ece9ac661f325aa51bb0b28d326063633227b/hw/xbox/mcpx/aci.c):
  LGPL2-or-later reference, no code copied into the driver.
- [Microsoft WDM audio stack](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/wave-and-directsound-components):
  waveOut uses WDMAud/SysAudio and KMixer feeding the port/miniport.
- [PortCls operating-system support](https://github.com/MicrosoftDocs/windows-driver-docs/blob/staging/windows-driver-docs-pr/audio/portcls-support-by-operating-system.md):
  WaveCyclic is supported on NT5; actual imported exports are still audited.
- [Synchronized interrupt callbacks](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/portcls/nf-portcls-iinterruptsync-callsynchronizedroutine):
  detach the ISR-visible pointer at interrupt synchronization level.
- [FreeCommonBuffer](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nc-wdm-pfree_common_buffer):
  allocation identity includes the same length used at allocation.

ReactOS AC97 sources at afc0127e8f937ab68503d715d948844973756aa1 include the
directory Microsoft MIT license and historical Microsoft/Intel file notices.
The incremental patch preserves those notices. Broader ReactOS components retain
their own licenses; this document does not relicense them. Downloaded reference
snapshots are private ignored inputs, while their provenance is tracked.

The inherited INF uses MEDIA class, exact `PCI\VEN_10DE&DEV_01B1`, KS/WDMAUDIO
registration, a demand-start PortCls service and Wave/Topology interfaces.
Initial207 testing replaces only that existing driver's binary plus test/startup
files. No INF/service/registry alteration is needed to test the lifecycle patch.
This does not validate fresh installation or the hardware codec.

The genuine installer uses the documented Windows2000-supported
[UpdateDriverForPlugAndPlayDevicesA](https://learn.microsoft.com/en-us/windows/win32/api/newdev/nf-newdev-updatedriverforplugandplaydevicesa)
with the full observed ACI hardware ID and a vendor-directory INF. Force-selection
is deliberate for the owned replacement test; no read-only or noninteractive flag
is used. A supplied reboot-result pointer leaves restart to the joined/idle runner.
[CM_Get_DevNode_Status](https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_get_devnode_status)
provides actual node flags/problem status. Both documented availability and actual
fixture exports/forwarders must be verified; documentation alone is not runtime
proof. Installation and subsequent persistent playback require separate cases.


The wave-only experiment follows Microsoft's [Topology Filters](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/topology-filters)
description of a minimal render WaveCyclic filter: two pins and a DAC. The fixed
hardware has no mixer controls that need a separate filter. Diagnostic002 located
a null dereference in the actualNT5 SysAudio graph-building path with the earlier
node-less topology filter. This motivates, but does not by itself validate, the
single-filter experiment. [Device-specific nodes](https://learn.microsoft.com/en-us/windows-hardware/drivers/audio/ksnodetype-dev-specific)
require a real device-specific property; a dummy node is not a substitute.


The driver links ReactOS stdunk, libcntpr, uuid and GCC support in addition to
import libraries. In particular sdk/lib/drivers/sound/stdunk/cunknown.cpp refers
to the root COPYING (GPL2). The Microsoft AC97 directory's MIT license does not
license the entire resulting binary. Preserve the root/component licenses and
full pinned source/build provenance in any package; do not label the whole binary
MIT merely because the edited driver directory carries that license.
