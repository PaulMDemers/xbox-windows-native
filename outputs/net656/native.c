/* SPDX-License-Identifier: GPL-2.0-or-later
 * Native I/O binding. Currently compiled but NOT hooked into the boot path.
 * No interrupt, mapping or MTRR writes. WBINVD is an explicit post-capture
 * transport effect, used for owned descriptor/buffer DMA visibility.
 */
#include "boot.h"
#include "nic.h"
#include "admission.h"
extern unsigned char _bss[],BSS_END[];
/* These existing WORD helpers are defined in drivers/pci/pci.c but omitted
 * from the legacy public header. Use their exact declarations, not implicit int.
 */
extern u16 PciReadWord(unsigned int,unsigned int,unsigned int,unsigned int);
extern void PciWriteWord(unsigned int,unsigned int,unsigned int,unsigned int,u16);
static struct dma656 Dma656 __attribute__((aligned(32)));
struct admission656 NativeAdmission656;
struct result656 NativeResult656;
unsigned NativeAdmissionError656;
static void msr(unsigned index,uint32_t *v){
 __asm__ __volatile__("rdmsr":"=a"(v[0]),"=d"(v[1]):"c"(index):"memory");
}
static int mmio_read(void *p,unsigned reg,uint32_t *value){
 (void)p;if((reg&3) || reg>=0x270)return -1;
 *value=*(volatile uint32_t *)(0xfef00000u+reg);return 0;
}
static int mmio_write(void *p,unsigned reg,uint32_t value){
 (void)p;if((reg&3) || reg>=0x270)return -1;
 *(volatile uint32_t *)(0xfef00000u+reg)=value;return 0;
}
static int command_write(void *p,uint16_t value){
 (void)p;PciWriteWord(0,4,0,4,value);return PciReadWord(0,4,0,4)!=value;
}
static uint32_t timer_read(void *p){(void)p;return IoInputDword(0x8008);}
static void cache_sync(void *p){(void)p;__asm__ __volatile__("wbinvd":::"memory");}
static int inspect(void){
 struct admission656 *a=&NativeAdmission656;
 struct {uint16_t limit;uint32_t base;} __attribute__((packed)) gdt;
 unsigned x,b,c,d,i;uint16_t cs,ds,es,ss;
 __asm__ __volatile__("mov %%cr0,%0":"=r"(a->cr0));
 __asm__ __volatile__("pushfl;popl %0":"=r"(a->flags)::"memory");
 __asm__ __volatile__("mov %%esp,%0":"=r"(a->esp));
 __asm__ __volatile__("cpuid":"=a"(x),"=b"(b),"=c"(c),"=d"(d):"a"(1):"memory");
 a->cpuid_edx=d;a->ram=xbox_ram*1024u*1024u;
 if((a->cr0&0xe0000001u)!=1 || (a->flags&0x200) || (d&0x1020)!=0x1020)return A656_CPU;
 __asm__ __volatile__("sgdt %0":"=m"(gdt));
 __asm__ __volatile__("mov %%cs,%0":"=r"(cs));
 __asm__ __volatile__("mov %%ds,%0":"=r"(ds));
 __asm__ __volatile__("mov %%es,%0":"=r"(es));
 __asm__ __volatile__("mov %%ss,%0":"=r"(ss));
 a->gdt_base=gdt.base;a->gdt_limit=gdt.limit;a->cs=cs;a->ds=ds;a->es=es;a->ss=ss;
 if(gdt.base!=0xa0000 || gdt.limit<31 || gdt.limit>4095 || cs!=0x10 || ds!=0x18 || es!=0x18 || ss!=0x18)return A656_SEGMENT;
 for(i=0;i<2;i++){a->code[i]=*(volatile uint32_t *)(0xa0010+4*i);a->data[i]=*(volatile uint32_t *)(0xa0018+4*i);}
 msr(0xfe,a->mtrr_cap);if((a->mtrr_cap[0]&255)!=8)return A656_CACHE;
 msr(0x2ff,a->mtrr_default);for(i=0;i<16;i++)msr(0x200+i,a->mtrr[i]);
 a->pci_id=PciReadDword(0,4,0,0);a->pci_bar=PciReadDword(0,4,0,0x10);a->command=PciReadWord(0,4,0,4);
 a->bss_begin=(uint32_t)_bss;a->bss_end=(uint32_t)BSS_END;
 a->dma_begin=(uint32_t)&Dma656;a->dma_bytes=sizeof(Dma656);
 return admission656(a);
}
/* Caller must supply frozen655 packet, EEPROM MAC, explicit configured source
 * IP/port, and call only AFTER capture. This dormant binding does not invent
 * any of those inputs or decide a success/failure/reset continuation.
 */
int NativeSend656(const uint8_t *packet,unsigned size,const uint8_t *mac,const uint8_t *source_ip,uint16_t port){
 struct io656 io={0,mmio_read,mmio_write,command_write,timer_read,cache_sync};
 struct plan656 plan={0};unsigned i;
 if(!packet || !mac || !source_ip || size!=772)return N656_ARGUMENT;
 if(NativeResult656.used)return N656_ALREADY;
 NativeAdmissionError656=inspect();if(NativeAdmissionError656)return N656_ARGUMENT;
 plan.dma_bus=(uint32_t)&Dma656;plan.command=NativeAdmission656.command;
 for(i=0;i<6;i++)plan.mac[i]=mac[i];
 for(i=0;i<4;i++)plan.source_ip[i]=source_ip[i];
 plan.port=port;plan.post_capture=1;plan.admitted=1;
 return send656(&io,&plan,&Dma656,packet,size,&NativeResult656);
}
