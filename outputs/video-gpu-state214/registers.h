/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reviewed214 observational offsets, sourced from pinned xemu model.
 * No read has GPU ownership or physical fidelity authority. */
#ifndef XGN_REGISTERS_H
#define XGN_REGISTERS_H
#define XGN_REGISTER_COUNT 22u
#define XGN_MAPPED_LENGTH 0x681000u
static const ULONG XgnOffsets[XGN_REGISTER_COUNT] = {
    0x00000000u, /* NV_PMC_BOOT_0 */
    0x00000100u, /* NV_PMC_INTR_0 */
    0x00000140u, /* NV_PMC_INTR_EN_0 */
    0x00002210u, /* NV_PFIFO_RAMHT */
    0x00002214u, /* NV_PFIFO_RAMFC */
    0x00002218u, /* NV_PFIFO_RAMRO */
    0x00002100u, /* NV_PFIFO_INTR_0 */
    0x00002140u, /* NV_PFIFO_INTR_EN_0 */
    0x00003200u, /* NV_PFIFO_CACHE1_PUSH0 */
    0x00003204u, /* NV_PFIFO_CACHE1_PUSH1 */
    0x00003220u, /* NV_PFIFO_CACHE1_DMA_PUSH */
    0x00003228u, /* NV_PFIFO_CACHE1_DMA_STATE */
    0x00003240u, /* NV_PFIFO_CACHE1_DMA_PUT */
    0x00003244u, /* NV_PFIFO_CACHE1_DMA_GET */
    0x00003250u, /* NV_PFIFO_CACHE1_PULL0 */
    0x00400100u, /* NV_PGRAPH_INTR */
    0x00400140u, /* NV_PGRAPH_INTR_EN */
    0x00400148u, /* NV_PGRAPH_CTX_USER */
    0x00400720u, /* NV_PGRAPH_FIFO */
    0x00600100u, /* NV_PCRTC_INTR_0 */
    0x00600140u, /* NV_PCRTC_INTR_EN_0 */
    0x00600800u, /* NV_PCRTC_START */
};
#endif
