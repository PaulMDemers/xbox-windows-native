# CR1A diagnostic alternative

815 wrote04, read2C and restored38.816 preserves every other saved bit and
sets only bit2 (saved38 OR04 =3C). All validation remains full-byte exact.
Haiku nvidia engine nv_crtc.c lines370-374 implements this read/modify/write
for widths below1280; Linux nouveau nvreg.h names RPC1 LARGE at bit2.
These references motivate a bounded diagnostic; they are not NV2A physical proof.
816 physical evidence validates this selected sequence only.

https://raw.githubusercontent.com/haiku/haiku/master/src/add-ons/accelerants/nvidia/engine/nv_crtc.c
https://kernel.googlesource.com/pub/scm/linux/kernel/git/will/linux/+/fdb9c3cd5124c9a6e4c824ed2bca5b4602e84a1a/drivers/gpu/drm/nouveau/nvreg.h
