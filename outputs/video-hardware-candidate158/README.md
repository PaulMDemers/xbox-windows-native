# Offline candidate for the next physical display trial

The Windows optimization already exists. RAM0112 copies actual complex-clip
intersections rather than gaps in their bounding box, retaining the earlier line
bounds fix. Ordinary real-window tests proved exact pixels and4.71% fewer movement
bytes/17.50% fewer repaint bytes. More copy calls mean a hardware speed gain is
still unmeasured. Windows156 measures an independent xemu improvement, not this
guest-driver comparison.

This review bundle contains the three exact files from the qualified Windows156
display chain: shared permanent UC bootvid provider, matching importing miniport,
and RAM0112 xwnown.dll. Module imports are checked against actual provider exports.
The boot loader loads xboxbvid.dll as bootvid.dll. Shared-provider runtime resolution
and acquisition were previously demonstrated; a lone xwnown.dll replacement does
not recreate that chain. No HAL/storage/network file or registry hive is packaged.

Private ZIPs are readback-verified and hashed in package-review.json. The rollback
ZIP contains qualified0093 miniport plus the unchanged Microsoft framebuf and historical bootvid from immutable0.1.0 archives,
not an entire historical SYSTEM hive. Its miniport/framebuf bytes match the last
physical0101 installed-state report. The historical bootvid provider has no entry
in that report: require fresh physical verification/backup before deployment.
Attempt157 correctly refused the older0.1.0 miniport as a0093 rollback; its failure is preserved. This NEW bundle uses the independently physical-qualified0093 artifact and checks it against the installed report. The archives and0.1.0 tag are unchanged. No FTP connection, deployment or boot was
performed to create this package.

deployment_ready and physical_qualified remain FALSE. Follow the explicit pending
steps in package-review.json. Review a supported display binding update to xwnown
using the actual physical keys/types; do not copy an emulator SYSTEM hive or its
synthetic null/unsupported-device policy. Reconstruct and validate the physical
driver chain in a new isolated emulator child before a bounded hardware trial.
Keep the existing physical FATX0101/video0093 baseline and0088 recovery available.
Probe real geometry first; the current emulator evidence is1024x576x32 only.

Additional modes, including1080i, and WC/GPU transfer acceleration remain separate
implementation work. This bundle changes no mode or cache policy and does not
claim generic PnP removal, crash rendering or physical scanout qualification.
