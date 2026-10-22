/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef XWN_ADMISSION656_H
#define XWN_ADMISSION656_H
#include <stdint.h>
struct admission656 {
 uint32_t cr0,flags,esp,ram,cpuid_edx;
 uint32_t gdt_base,gdt_limit,cs,ds,es,ss,code[2],data[2];
 uint32_t mtrr_cap[2],mtrr_default[2],mtrr[16][2];
 uint32_t pci_id,pci_bar,command,bss_begin,bss_end,dma_begin,dma_bytes;
};
enum admission_error656 { A656_OK,A656_CPU,A656_SEGMENT,A656_CACHE,A656_PCI,A656_DMA };
/* Exact retained native memory/cache contract; rejects rather than repairs. */
int admission656(const struct admission656 *);
#endif
