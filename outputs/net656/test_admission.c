/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "admission.h"
#include "nic.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 struct admission656 a={0},b;unsigned i,j,checks=0;
 a.cr0=0x10033;a.flags=2;a.esp=0x027ff000;a.ram=0x4000000;a.cpuid_edx=0x1020;
 a.gdt_base=0xa0000;a.gdt_limit=31;a.cs=0x10;a.ds=a.es=a.ss=0x18;
 a.code[0]=a.data[0]=0xffff;a.code[1]=0xcf9b00;a.data[1]=0xcf9300;
 a.mtrr_cap[0]=0x508;a.mtrr_default[0]=0x800;
 a.mtrr[0][0]=6;a.mtrr[1][0]=0xf8000800;a.mtrr[1][1]=15;
 a.mtrr[2][0]=0xf0000001;a.mtrr[3][0]=0xf8000800;a.mtrr[3][1]=15;
 a.mtrr[4][0]=0xfff00000;a.mtrr[5][0]=0xfff00800;a.mtrr[5][1]=15;
 a.pci_id=0x01c310de;a.pci_bar=0xfef00000;a.command=7;
 a.bss_begin=0x02650000;a.bss_end=0x02690000;a.dma_begin=0x02680000;a.dma_bytes=sizeof(struct dma656);
 assert(admission656(&a)==0);checks++;
 for(i=0;i<16;i++)for(j=0;j<64;j++){b=a;b.mtrr[i][j/32]^=1u<<(j%32);assert(admission656(&b)==A656_CACHE);checks++;}
 b=a;b.cr0|=0x80000000;assert(admission656(&b)==A656_CPU);checks++;
 b=a;b.flags|=0x200;assert(admission656(&b)==A656_CPU);checks++;
 b=a;b.data[1]|=0x10000000;assert(admission656(&b)==A656_SEGMENT);checks++;
 b=a;b.gdt_base=0xffffffff;assert(admission656(&b)==A656_SEGMENT);checks++;
 b=a;b.mtrr_cap[0]=9;assert(admission656(&b)==A656_CACHE);checks++;
 b=a;b.pci_id=0;assert(admission656(&b)==A656_PCI);checks++;
 b=a;b.command=0;assert(admission656(&b)==A656_PCI);checks++;
 b=a;b.dma_begin=0xffffffe0;assert(admission656(&b)==A656_DMA);checks++;
 b=a;b.bss_end=b.dma_begin+b.dma_bytes-1;assert(admission656(&b)==A656_DMA);checks++;
 b=a;b.dma_begin++;assert(admission656(&b)==A656_DMA);checks++;
 b=a;b.bss_begin=b.dma_begin+32;assert(admission656(&b)==A656_DMA);checks++;
 b=a;b.bss_end=b.dma_begin+b.dma_bytes;assert(admission656(&b)==0);checks++;
 printf("{\"checks\":%u,\"physical_context_sampled\":false}\n",checks);return 0;
}
