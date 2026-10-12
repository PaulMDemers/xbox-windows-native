# Next: coordinated Windows HD handoff

Preserve closed 291/292. Record the user's TV observation separately when it arrives. Do not infer visual quality from CRC or tag 0.2.0 yet.

The present Cromwell code at 58-60 MiB and stack at 60 MiB overlap a top-of-RAM HD reservation. Review a relocation-only candidate first: code in 38-40 MiB, stack below 40 MiB, retaining the existing 4 MiB framebuffer and low-resolution path. Verify the actual ELF/BSS end and stack headroom, every absolute startup/config/jump reference, and a fresh emulator handoff before any deployment. Preserve original launcher.

Future 1920x1080 32-bit pixels plus bootvid backing need 8,610,560 bytes, exceeding 8 MiB. A proposed 9 MiB reservation begins at 55 MiB, requiring an explicit Linux initrd-limit decision and coordinated FreeLdr/bootvid/shared-provider/miniport contract. No such implementation exists yet. Current 128 MiB memory-map path needs independent review.

292 FP registers alone do not capture all CRTC interlace/PLL/encoder state. Cromwell's fixed sync-end heuristics differ from actual kernel-programmed HD values. Obtain a complete pinned timing contract before programming HD. Stock API success does not establish Windows ownership or display handoff.
