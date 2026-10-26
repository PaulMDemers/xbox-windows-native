# 683: HDMI720p kernel baseline prepared

Fresh watched diagnostic for the incoming user-identified1.6 after682 composite.
Requests1280x720x32 at60Hz only for kernel-reported NTSC-M/J, HDTV AV pack,
720p enabled and64MiB. Retains observed geometry guards for1280x720/5120-byte
stride/32-bit format; draws through the SDK-owned framebuffer. Pattern remains
20seconds then requests dashboard return. Kernel calls are not application-bounded.
User must watch and be available to reset. No startup hook or Windows install.

Build001 compiled under the shared build lease with existing nxdk. The existing
linker section-merge warning remains. Host001 passed3,145,728 extracted admission
assertions and the extracted1280x720 drawing loop under ASan/UBSan, including
framebuffer boundary canaries. These are host checks, not an Xbox execution or
native Xcalibur/Windows qualification. Exact test source is test_admission.c.

Private XBE: C:/xwn683/build001/bin/default.xbe. Source/build/controller pins are
retained here. At preparation there is no staging or launch. Read the latest
continuation and any later ready/stage/launch/collection records for live state.

## Next

1. Await user HDMI-connected dashboard readiness and720p setting; record it in
   ready001.json. Revalidate the current endpoint, ticket and free space.
2. Review the controller and all pins; stage/read back a fresh owned E directory.
   Send one SITE command with a20-second reply limit. Never retry an accepted or
   uncertain request.
3. Ask for visible pattern, colors, border/clipping and automatic return. Allow
   time for the20-second display and reboot before connecting. A user manual
   launch must be recorded separately; collect all new report sequences without
   overwriting failed collection records.
4. Treat GPU values as observations. Do not transplant kernel state into the
   native profile or promote Windows support from this kernel-only baseline.
