/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "pio.h"
static uint16_t word(const uint8_t *p,unsigned n){return (uint16_t)(p[n*2]|((uint16_t)p[n*2+1]<<8));}
static int fail(struct pio653 *c,int r){c->poisoned=1;return r;}
int map653(const struct plan653 *p) {
    unsigned i,j;uint32_t end;
    if(!p || !p->disk_sectors || p->disk_sectors>0x10000000u ||
       !p->partition_start || !p->partition_sectors ||
       p->partition_start>=p->disk_sectors ||
       p->partition_sectors>p->disk_sectors-p->partition_start)return MAP653;
    end=p->partition_start+p->partition_sectors;
    if(p->data_start<=p->partition_start || p->data_start>=end ||
       !p->poll_limit || p->poll_limit>65536)return MAP653;
    for(i=0;i<3;i++) {
        if(p->sector[i]<p->data_start || p->sector[i]>=end)return MAP653;
        for(j=0;j<i;j++)if(p->sector[i]==p->sector[j])return MAP653;
    }
    return OK653;
}
static int r8(struct pio653 *c,unsigned reg,uint8_t *v) {
    if(c->io.read8(c->io.opaque,reg,v))return fail(c,IO653);
    return OK653;
}
static int bus(struct pio653 *c,int initial) {
    uint8_t command,status;
    if(c->io.flags(c->io.opaque)&0x200u)return fail(c,BUS653);
    if(r8(c,BM_COMMAND653,&command)||r8(c,BM_STATUS653,&status))return IO653;
    c->last_bm=status;
    if(command==255 || status==255 || (command&1) ||
       (status&(initial?7:3)))return fail(c,BUS653);
    return OK653;
}
static int settle(struct pio653 *c) {
    if(c->io.settle(c->io.opaque))return fail(c,IO653);
    return OK653;
}
/* Poll Alternate Status, then explicitly acknowledge OUR command's interrupt
 * through Status only when no longer busy. Never interpret ERR/DF while BSY.
 * Idle admission uses acknowledge=0, so a preexisting interrupt isn't cleared.
 */
static int wait653(struct pio653 *c,int need_drq,int acknowledge) {
    unsigned i;uint8_t v;int r;
    for(i=0;i<c->plan.poll_limit;i++) {
        if((r=bus(c,0)))return r;
        if(r8(c,ALT653,&v))return IO653;
        c->last_status=v;c->status_reads++;
        if(v==0 || v==255)return fail(c,STATUS653);
        if(v&0x80)continue;
        if(v&0x21)return fail(c,STATUS653);
        if(!(v&0x40))continue;
        if(need_drq && !(v&8))continue;
        if(!need_drq && (v&8))return fail(c,STATUS653);
        if(acknowledge) {
            if(r8(c,STATUS_COMMAND653,&v))return IO653;
            c->ack_reads++;c->last_status=v;
            if((v&0xe1)!=0x40 || ((v&8)!=0)!=need_drq)return fail(c,STATUS653);
        }
        return OK653;
    }
    return fail(c,TIMEOUT653);
}
static int w8(struct pio653 *c,unsigned reg,uint8_t v) {
    if(c->io.write8(c->io.opaque,reg,v))return fail(c,IO653);
    return OK653;
}
static int command653(struct pio653 *c,uint8_t cmd,uint32_t lba,uint8_t *readbuf,const uint8_t *writebuf) {
    unsigned i;int r;uint16_t v;
    if((r=wait653(c,0,0)))return r;
    /* Selection/task-file writes occur only after idle readiness. */
    if(w8(c,DEVICE653,(uint8_t)(0xe0u|(lba>>24))))return IO653;
    if((r=settle(c)) || (r=wait653(c,0,0)))return r;
    if(cmd!=0xe7 && cmd!=0xec) {
        if(w8(c,COUNT653,1)||w8(c,LBA0653,(uint8_t)lba)||
           w8(c,LBA1653,(uint8_t)(lba>>8))||w8(c,LBA2653,(uint8_t)(lba>>16)))return IO653;
    }
    /* A command write may have taken effect even on error: consume it first. */
    c->commands++;
    if(w8(c,STATUS_COMMAND653,cmd))return IO653;
    if((r=settle(c)))return r;
    if(cmd==0xe7)return wait653(c,0,1);
    if((r=wait653(c,1,1)))return r;
    for(i=0;i<256;i++) {
        if((r=bus(c,0)))return r;
        if(writebuf) {
            v=(uint16_t)(writebuf[2*i]|((uint16_t)writebuf[2*i+1]<<8));
            if(c->io.write16(c->io.opaque,DATA653,v))return fail(c,IO653);
        } else {
            if(c->io.read16(c->io.opaque,DATA653,&v))return fail(c,IO653);
            readbuf[2*i]=(uint8_t)v;readbuf[2*i+1]=(uint8_t)(v>>8);
        }
        c->data_words++;
    }
    if((r=settle(c)))return r;
    return wait653(c,0,1);
}
int admit653(struct pio653 *c,const struct io653 *io,const struct plan653 *plan,const uint8_t *expected) {
    uint8_t actual[512];unsigned i;uint32_t capacity;int r;
    if(!c || !io || !io->read8 || !io->read16 || !io->write8 || !io->write16 ||
       !io->settle || !io->flags || !expected)return ARG653;
    /* Caller must supply a fresh zeroed context. Admission itself is one-shot. */
    if(c->poisoned || c->admitted || c->commands)return POISON653;
    c->poisoned=1;
    if((r=map653(plan)))return r;
    if(plan->permit_status_ack!=1)return POLICY653;
    c->io=*io;c->plan=*plan;
    if((r=bus(c,1)))return r;
    if((r=command653(c,0xec,0,actual,0)))return r;
    for(i=0;i<512;i++)if(actual[i]!=expected[i])return IDENTITY653;
    capacity=(uint32_t)word(actual,60)|((uint32_t)word(actual,61)<<16);
    if((word(actual,0)&0x8000) || !(word(actual,49)&0x200) ||
       (word(actual,83)&0xd000)!=0x5000 || capacity!=plan->disk_sectors ||
       ((word(actual,106)&0xc000)==0x4000 && (word(actual,106)&0x1000)))return IDENTITY653;
    c->admitted=1;c->poisoned=0;return OK653;
}
static int next(struct pio653 *c,unsigned op,unsigned slot) {
    static const uint8_t ops[13]={0,0,0,1,1,2,0,0,1,2,0,0,0};
    static const uint8_t slots[13]={0,1,2,0,1,0,0,1,2,0,0,1,2};
    if(!c || c->poisoned || !c->admitted)return POISON653;
    if(c->step>=13 || op!=ops[c->step] || slot!=slots[c->step])return fail(c,ORDER653);
    c->step++;return OK653;
}
int read653(void *o,unsigned slot,uint8_t *p) {
    struct pio653 *c=o;int r;
    if(!p)return c?fail(c,ARG653):ARG653;
    if((r=next(c,0,slot)))return r;
    return command653(c,0x20,c->plan.sector[slot],p,0);
}
int write653(void *o,unsigned slot,const uint8_t *p) {
    struct pio653 *c=o;int r;
    if(!p)return c?fail(c,ARG653):ARG653;
    if((r=next(c,1,slot)))return r;
    return command653(c,0x30,c->plan.sector[slot],0,p);
}
int flush653(void *o) {
    struct pio653 *c=o;int r;
    if((r=next(c,2,0)))return r;
    return command653(c,0xe7,0,0,0);
}
