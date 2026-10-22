/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "admission.h"
#include "nic.h"
int admission656(const struct admission656 *a){
 static const uint32_t expected[6][2]={
  {6,0},{0xf8000800u,15},{0xf0000001u,0},{0xf8000800u,15},
  {0xfff00000u,0},{0xfff00800u,15}};
 unsigned i;
 if(!a || (a->cr0&0xe0000001u)!=1 || (a->flags&0x200) ||
    (a->cpuid_edx&0x1020)!=0x1020 || (a->ram!=0x4000000 && a->ram!=0x8000000) ||
    a->esp<0x027c0000 || a->esp>=0x02800000)return A656_CPU;
 if(a->gdt_base!=0xa0000 || a->gdt_limit<31 || a->gdt_limit>4095 ||
    a->cs!=0x10 || a->ds!=0x18 || a->es!=0x18 || a->ss!=0x18 ||
    a->code[0]!=0xffff || (a->code[1]&~0x100u)!=0xcf9a00 ||
    a->data[0]!=0xffff || (a->data[1]&~0x100u)!=0xcf9200)return A656_SEGMENT;
 if((a->mtrr_cap[0]&255)!=8 || a->mtrr_default[0]!=0x800 || a->mtrr_default[1])return A656_CACHE;
 for(i=0;i<6;i++)if(a->mtrr[i][0]!=expected[i][0] || a->mtrr[i][1]!=expected[i][1])return A656_CACHE;
 for(i=6;i<16;i++)if(a->mtrr[i][0] || a->mtrr[i][1])return A656_CACHE;
 if(a->pci_id!=0x01c310de || (a->pci_bar&~15u)!=0xfef00000u || (a->pci_bar&1) ||
    (a->command&2)==0 || a->command>65535)return A656_PCI;
 if(a->bss_begin<0x02600000 || a->bss_end>0x027c0000 || a->bss_end<a->bss_begin ||
    a->dma_begin<a->bss_begin || a->dma_begin>a->bss_end || (a->dma_begin&31) ||
    a->dma_bytes!=sizeof(struct dma656) || a->dma_bytes>a->bss_end-a->dma_begin)return A656_DMA;
 return 0;
}
