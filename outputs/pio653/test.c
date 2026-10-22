/* SPDX-License-Identifier: GPL-2.0-or-later. RAM-only device model. */
#include "pio.h"
#include "receipt.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct model {
    uint8_t cache[1536],disk[1536],identify[512],task[10];
    unsigned calls,fail_at,after,commands,word_index,task_writes,sector_writes;
    unsigned ack,irq,last_command,lba,initial_bm,initial_flags;
    unsigned target,fault,delay,polls,settles;
};
static struct plan653 plan={100000,1000,10000,1100,{1200,1300,1400},8,1};
static struct xwn652_identity identity;
static struct xwn652_data data;
static unsigned checks;
static int begin(struct model *m){m->calls++;return m->calls==m->fail_at && !m->after;}
static int end(struct model *m){return m->calls==m->fail_at && m->after;}
static uint8_t status(struct model *m,int consume) {
    if(m->commands==m->target && m->target) {
        if(m->fault==1)return 0xa1; /* BSY: ERR/DF must not be used yet. */
        if(m->fault==2)return 0x40; /* No DRQ. */
        if(m->fault==3)return 0x41;
        if(m->fault==4)return 0x60;
        if(m->fault==5)return 0;
        if(m->fault==6)return 255;
        if(m->fault==7 && m->word_index==256)return 0x48;
        if(m->fault==8 && m->word_index==256)return 0x41;
        if(m->word_index==0 && m->polls<m->delay) {
            if(consume)m->polls++;
            return 0x80;
        }
    }
    if(m->last_command && m->last_command!=0xe7 && m->word_index<256)return 0x48;
    return 0x40;
}
static int read8(void *o,unsigned reg,uint8_t *v) {
    struct model *m=o;assert(reg==ALT653 || reg==STATUS_COMMAND653 || reg==BM_COMMAND653 || reg==BM_STATUS653);
    if(begin(m))return 1;
    if(reg==BM_COMMAND653)*v=(m->fault==9 && m->commands==m->target)?1:0;
    else if(reg==BM_STATUS653) {
        *v=(uint8_t)(m->commands?4:m->initial_bm);
        if(m->fault==10 && m->commands==m->target)*v|=1;
        if(m->fault==11 && m->commands==m->target)*v|=2;
    } else {
        *v=status(m,reg==ALT653);
        if(reg==STATUS_COMMAND653){assert(m->commands);m->ack++;m->irq=0;}
    }
    return end(m);
}
static unsigned slot(struct model *m) {
    unsigned i;for(i=0;i<3;i++)if(plan.sector[i]==m->lba)return i;
    assert(0);return 0;
}
static int read16(void *o,unsigned reg,uint16_t *v) {
    struct model *m=o;const uint8_t *p;
    assert(reg==DATA653 && m->word_index<256 && status(m,0)==0x48);
    assert(m->last_command==0xec || m->last_command==0x20);
    if(begin(m))return 1;
    p=m->last_command==0xec?m->identify:m->cache+512*slot(m);
    *v=(uint16_t)(p[m->word_index*2]|((uint16_t)p[m->word_index*2+1]<<8));
    m->word_index++;return end(m);
}
static int write8(void *o,unsigned reg,uint8_t v) {
    struct model *m=o;
    assert(reg==DEVICE653 || reg==COUNT653 || reg==LBA0653 || reg==LBA1653 || reg==LBA2653 || reg==STATUS_COMMAND653);
    if(begin(m))return 1;
    m->task_writes++;m->task[reg]=v;
    if(reg==STATUS_COMMAND653) {
        assert(v==0xec || v==0x20 || v==0x30 || v==0xe7);
        m->commands++;m->last_command=v;m->word_index=0;m->polls=0;m->irq=1;
        if(v==0x20 || v==0x30) {
            assert(m->task[COUNT653]==1 && (m->task[DEVICE653]&0xf0)==0xe0);
            m->lba=m->task[LBA0653]|((unsigned)m->task[LBA1653]<<8)|((unsigned)m->task[LBA2653]<<16)|((unsigned)(m->task[DEVICE653]&15)<<24);
            (void)slot(m);
        }
        if(v==0xe7)memcpy(m->disk,m->cache,1536);
    }
    return end(m);
}
static int write16(void *o,unsigned reg,uint16_t v) {
    struct model *m=o;uint8_t *p;
    assert(reg==DATA653 && m->last_command==0x30 && m->word_index<256 && status(m,0)==0x48);
    if(begin(m))return 1;
    p=m->cache+512*slot(m)+2*m->word_index;
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);m->word_index++;m->sector_writes++;
    return end(m);
}
static int settle(void *o){struct model *m=o;if(begin(m))return 1;m->settles++;return end(m);}
static uint32_t flags(void *o){struct model *m=o;m->calls++;return (m->calls==m->fail_at)?0x202:m->initial_flags;}
static void setword(uint8_t *p,unsigned i,unsigned v){p[2*i]=(uint8_t)v;p[2*i+1]=(uint8_t)(v>>8);}
static void init(struct model *m) {
    unsigned i;memset(m,0,sizeof(*m));m->initial_flags=2;
    setword(m->identify,0,0x40);setword(m->identify,49,0x200);setword(m->identify,83,0x5000);
    setword(m->identify,60,plan.disk_sectors&65535);setword(m->identify,61,plan.disk_sectors>>16);
    for(i=0;i<3;i++)xwn652_seed(&identity,i,m->cache+512*i);
    memcpy(m->disk,m->cache,1536);
}
static int run(struct model *m,struct pio653 *c,int *admitted) {
    struct io653 io={m,read8,read16,write8,write16,settle,flags};
    struct xwn652_io sink={c,read653,write653,flush653};
    struct xwn652_scratch scratch;struct xwn652_guard guard={0};
    uint8_t expected[512];int r;
    memcpy(expected,m->identify,512);memset(c,0,sizeof(*c));
    r=admit653(c,&io,&plan,expected);*admitted=!r;
    if(r)return r;
    return xwn652_store(&guard,&sink,&identity,&data,&scratch);
}
int main(void) {
    struct model m;struct pio653 c;unsigned i,j,total;int r,admitted;
    uint8_t expected[512],temp[512];struct io653 io={&m,read8,read16,write8,write16,settle,flags};
    struct plan653 bad;
    for(i=0;i<16;i++)identity.attempt[i]=(uint8_t)(i+1);
    for(i=0;i<32;i++)identity.candidate_sha256[i]=(uint8_t)(i+0x80);
    data.result=-1;data.post_kind=2;
    init(&m);assert(run(&m,&c,&admitted)==0 && admitted);
    assert(c.step==13 && c.commands==14 && m.commands==14 && m.sector_writes==768);
    assert(c.data_words==3072 && m.ack==26 && c.ack_reads==26);
    assert(xwn652_validate(&identity,m.disk));checks++;total=m.calls;
    /* Fault each low-level call before/after: no subsequent callback is issued. */
    for(i=1;i<=total;i++)for(j=0;j<2;j++) {
        unsigned old;init(&m);m.fail_at=i;m.after=j;r=run(&m,&c,&admitted);
        assert(r && c.poisoned && m.calls==i);old=m.calls;
        assert(read653(&c,0,temp)==POISON653 && m.calls==old);checks++;
    }
    /* Every command sees protocol errors; no recovery or second command. */
    for(i=1;i<=14;i++)for(j=1;j<=11;j++) {
        if(j==2 && (i==7 || i==11))continue; /* flush has no DRQ */
        if((j==7 || j==8) && (i==7 || i==11))continue;
        init(&m);m.target=i;m.fault=j;r=run(&m,&c,&admitted);
        assert(r && c.poisoned && m.commands==i);checks++;
    }
    /* Last permitted ready sample accepted; one sample later is refused. */
    for(i=1;i<=14;i++)if(i!=7 && i!=11) {
        init(&m);m.target=i;m.delay=plan.poll_limit-1;assert(!run(&m,&c,&admitted));checks++;
        init(&m);m.target=i;m.delay=plan.poll_limit;assert(run(&m,&c,&admitted) && c.poisoned);checks++;
    }
    for(i=0;i<8;i++)if(i) {
        init(&m);m.initial_bm=i;assert(run(&m,&c,&admitted)==BUS653 && !m.task_writes);checks++;
    }
    init(&m);m.initial_flags=0x202;assert(run(&m,&c,&admitted)==BUS653 && !m.task_writes);checks++;
    /* Policy refusal happens before any hardware callback. */
    init(&m);memcpy(expected,m.identify,512);memset(&c,0,sizeof(c));bad=plan;bad.permit_status_ack=0;
    assert(admit653(&c,&io,&bad,expected)==POLICY653 && !m.calls);checks++;
    /* Foreign identity, unsupported flush and wrong capacity refuse sector I/O. */
    for(i=0;i<512;i++) {
        init(&m);memcpy(expected,m.identify,512);expected[i]^=1;memset(&c,0,sizeof(c));
        assert(admit653(&c,&io,&plan,expected)==IDENTITY653 && m.commands==1 && !m.sector_writes);checks++;
    }
    for(i=0;i<5;i++) {
        init(&m);if(i==0)setword(m.identify,0,0x8000);if(i==1)setword(m.identify,49,0);
        if(i==2)setword(m.identify,83,0x4000);
        if(i==3)setword(m.identify,60,1);
        if(i==4)setword(m.identify,106,0x5000);
        memcpy(expected,m.identify,512);memset(&c,0,sizeof(c));
        assert(admit653(&c,&io,&plan,expected)==IDENTITY653 && m.commands==1);checks++;
    }
    /* Geometry independently constrains the caller-supplied three-sector map. */
    for(i=0;i<9;i++) {
        bad=plan;
        if(i==0)bad.disk_sectors=0;
        if(i==1)bad.disk_sectors=0x10000001;
        if(i==2)bad.partition_start=0xffffffffu;
        if(i==3)bad.partition_sectors=0xffffffffu;
        if(i==4)bad.data_start=bad.partition_start;
        if(i==5)bad.sector[0]=bad.data_start-1;
        if(i==6)bad.sector[1]=bad.sector[2];
        if(i==7)bad.sector[2]=bad.partition_start+bad.partition_sectors;
        if(i==8)bad.poll_limit=65537;
        assert(map653(&bad)==MAP653);checks++;
    }
    init(&m);memcpy(expected,m.identify,512);memset(&c,0,sizeof(c));assert(!admit653(&c,&io,&plan,expected));
    i=m.calls;assert(write653(&c,0,temp)==ORDER653 && c.poisoned && m.calls==i);checks++;
    printf("{\"passed\":true,\"checks\":%u,\"success_low_level_calls\":%u,\"physical_access\":false}\n",checks,total);
    return 0;
}
