/* SPDX-License-Identifier: GPL-2.0-or-later
 * Explicit Conexant HDTV timing profiles for the reviewed 64MiB/9MiB handoff.
 * Pure data preparation: NO hardware access or encoder readback assumptions.
 */
#ifndef XWN_HD_PROFILE310_H
#define XWN_HD_PROFILE310_H
#include <stdint.h>
enum xwn_hd_mode { XWN_HD_720P=1, XWN_HD_1080I=2 };
struct xwn_hd_profile {
 uint32_t width,height,stride,visible_bytes,interlaced;
 uint8_t crtc[35];
 uint32_t mmio[28];
 uint8_t encoder[14];
};
extern const uint8_t xwn_hd_crtc_indices[35];
extern const uint32_t xwn_hd_mmio_offsets[28];
extern const uint8_t xwn_hd_encoder_indices[14];
/* Invalid mode/output leaves caller storage unchanged. */
int xwn_hd_get_profile(unsigned mode,struct xwn_hd_profile *out);
/* Exact reviewed ABI2 memory layout only. Geometry comes from selected profile,
 * not analog HVALID or an arbitrary caller-supplied stride. */
int xwn_hd_layout_valid(unsigned mode,uint32_t ram_bytes,uint32_t fb_start,
                        uint32_t reserved_bytes,uint32_t hidden_bytes);
#endif
