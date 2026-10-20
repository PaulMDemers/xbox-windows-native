# User-supplied Xbox 1.6 inventory

The user identifies this console as revision 1.6. The attached schema-2 report
passes tools/hardware_report.py, including xbox-safe-v1 PCI exclusions and field
validation. The exact input bytes and hash are retained. This is an inventory
observation, not a new agent-controlled launch or Windows qualification.

- Kernel: 1.0.5838.1. Kernel-reported memory: 16,384 pages of 4,096 bytes = 64 MiB.
- GPU revision: 225 (0xe1); MCP revision: 213 (0xd5). These are raw observations.
- Both Conexant and Focus probes returned 0xc0000185. The encoder label is
  correctly unidentified. Returned value fields from failed reads do not identify
  a device. This tool does not positively probe Xcalibur.
- Current mode enumeration lists 640x480 and 720x480, both 32-bit at 60 Hz.
  It lists no 720p mode. This reflects the observed configuration, not a claim
  that the motherboard cannot output 720p. The list omits interlace flags, so
  it does not distinguish 480i from 480p here.
- Dashboard E reports 4,353,671,168 bytes free (about 4.05 GiB), above the delivery587
  package's stated 1.25 GiB admission requirement. Recheck before staging; space
  alone does not establish profile or hardware compatibility.
- There are 63 PCI response records. Function aliases mean this is not a count
  of independent devices.

The 64-MiB observation matches one prerequisite of the current HD reservation.
The encoder and current mode enumeration do not match the qualified development
console profile. Do not infer Xcalibur merely from those two failed probes or
compare raw nxdk AV-pack codes directly with Cromwell's differently represented
cable field. The legacy Xromwell fallback remains a review item from629.

Next: obtain the cable/HDMI-adapter and dashboard HD-setting context (asked once),
then establish the encoder-specific boot/display path for this user-reported1.6.
A matching Windows profile still requires source/build review and watched hardware
qualification. No Windows test or tool auto-return observation was provided.
Keep the original development console's working720p package unchanged. Physical
RCT measurement there remains pending; acceleration follows revision work.
