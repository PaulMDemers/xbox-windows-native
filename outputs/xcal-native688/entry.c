/* SPDX-License-Identifier: GPL-2.0-or-later
 * Host-only full-image entry diagnostic. NOT a physical launch candidate.
 * Stops before PCI init, legacy SMBus, GPU setup or any Windows path.
 * No encoder/EEPROM/SMC configuration writes. CF8 is selected then restored.
 * SMBus reads use687's checked operations and acknowledge only owned results.
 */
#include "entry.h"
#include "xcal_bus.h"
int native_config_read(uint8_t,uint8_t,uint8_t *);
int native_read(uint8_t,uint32_t *);
volatile struct entry688 XcalState688;
static uint32_t in32(uint16_t p)
{uint32_t v;__asm__ volatile("inl %w1,%0":"=a"(v):"d"(p):"memory");return v;}
static uint16_t in16(uint16_t p)
{uint16_t v;__asm__ volatile("inw %w1,%0":"=a"(v):"d"(p):"memory");return v;}
static void out32(uint16_t p,uint32_t v)
{__asm__ volatile("outl %0,%w1"::"a"(v),"d"(p):"memory");}
static uint32_t pci(uint32_t selector)
{out32(0xcf8,selector);return in32(0xcfc);}
static int byte(volatile struct entry688 *s,uint8_t a,uint8_t reg,uint8_t *v)
{
    s->failed_address=a;s->failed_register=reg;
    int e=native_config_read(a,reg,v);
    if(e){s->error=e;return 0;}
    ++s->completed;return 1;
}
int XcalCollect688(volatile struct entry688 *s)
{
    uint32_t v;uint16_t seg;uint8_t b;
    *s=(struct entry688){0};s->magic=0x584e0688;s->phase=1;
    __asm__ volatile("pushfl;popl %0":"=r"(v)::"memory");s->flags=v;
    __asm__ volatile("mov %%cr0,%0":"=r"(v));s->cr0=v;
    __asm__ volatile("mov %%cr3,%0":"=r"(v));s->cr3=v;
    __asm__ volatile("mov %%cr4,%0":"=r"(v));s->cr4=v;
    __asm__ volatile("mov %%cs,%0":"=r"(seg));s->cs=seg;
    __asm__ volatile("mov %%ds,%0":"=r"(seg));s->ds=seg;
    __asm__ volatile("mov %%ss,%0":"=r"(seg));s->ss=seg;
    if((s->flags&0x200) || (s->cr0&0x80000001)!=1 ||
       s->cs!=0x10 || s->ds!=0x18 || s->ss!=0x18) {
        s->error=E688_CONTEXT;return 0;
    }
    s->phase=2;s->pci_selector=in32(0xcf8);
    s->pci_id=pci(0x80000900);s->pci_command=pci(0x80000904);
    s->pci_bar=pci(0x80000914);out32(0xcf8,s->pci_selector);
    if(s->pci_id!=0x01b410de){s->error=E688_DEVICE;return 0;}
    if(!(s->pci_command&1) || s->pci_bar!=0xc001) {
        s->error=E688_MAPPING;return 0;
    }
    s->phase=3;s->status_before=in16(0xc000);
    if(s->status_before&0x800){s->error=XCAL_BUSY;return 0;}
    if(s->status_before&0x36){s->error=XCAL_DIRTY_STATUS;return 0;}
    s->phase=4;
    if(!byte(s,0x10,4,&b))return 0;s->cable=b;
    for(unsigned i=0;i<4;++i) {
        if(!byte(s,0x54,0x58+i,&b))return 0;
        s->standard|=(uint32_t)b<<(i*8);
    }
    if(!byte(s,0x54,0x96,&b))return 0;s->video_flags=b;
    if(s->cable!=1 || (s->standard!=0x00400100 && s->standard!=0x00400200) ||
       !(s->video_flags&8)){s->error=E688_CONFIG;return 0;}
    s->phase=5;s->failed_address=0x70;s->failed_register=0;
    int error=native_read(0,&v);
    if(error){s->error=error;return 0;}
    s->encoder_value=v;++s->completed;s->status_after=in16(0xc000);
    if(s->status_after&0x836){s->error=XCAL_DIRTY_STATUS;return 0;}
    s->failed_address=0;s->failed_register=0;s->phase=6;return 1;
}
void XcalEntry688(void)
{
    (void)XcalCollect688(&XcalState688);
    /* No CLI, reset, indicator write or fallthrough into unreviewed startup. */
    for(;;)__asm__ volatile("hlt":::"memory");
}
