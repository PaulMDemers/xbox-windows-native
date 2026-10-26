/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "xcal_profile.h"
#include "xcal_table.h"
#include "../../src/utilities/video-baseline/pattern.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct model {
    unsigned calls, writes, commands, polls, fifo, delays, fails_at, delay_fail;
    unsigned count, initial, status, address, reg, command;
    unsigned nbytes; uint8_t bytes[4];
    unsigned regs[148], addresses[148], cmds[148]; uint32_t words[148];
};
static uint8_t r8(void *v, unsigned port)
{
    struct model *m=v; ++m->calls;
    if (port==0) { ++m->polls; return m->fails_at==m->commands ? 0x36 : m->status; }
    assert(port==9 && m->fifo<4);
    static const uint8_t response[4]={0x12,0x34,0x56,0x78};
    return response[m->fifo++];
}
static uint16_t r16(void *v, unsigned port)
{ struct model *m=v; ++m->calls; assert(port==0 || port==6); return port==0 ? m->initial : m->count; }
static void w8(void *v, unsigned port, uint8_t value)
{
    struct model *m=v; ++m->calls; ++m->writes;
    if(port==4) {m->address=value; m->nbytes=0; m->fifo=0;}
    else if(port==8) m->reg=value;
    else if(port==9) {assert(m->nbytes<4);m->bytes[m->nbytes++]=value;}
    else {
        assert(port==2 && m->commands<148);
        unsigned i=m->commands++; m->cmds[i]=value;m->regs[i]=m->reg;m->addresses[i]=m->address;
        m->words[i]=0;
        for(unsigned j=0;j<m->nbytes;++j)m->words[i]|=(uint32_t)m->bytes[j]<<(8*j);
        if(value==0x1d) assert(m->nbytes==4);
        else assert(value==0x0d && m->nbytes==0);
    }
}
static void w16(void *v, unsigned port, uint16_t value)
{ struct model *m=v; ++m->calls; ++m->writes; assert((port==6 && value==4) || (port==0 && value==(m->fails_at==m->commands?0x36:(m->status & 0x36)))); }
static int pause500(void *v)
{struct model *m=v; ++m->delays; return m->delays!=m->delay_fail;}
static struct xcal_bus bus(struct model *m)
{struct xcal_bus b={m,r8,r16,w8,w16,7};return b;}
static struct model fresh(void)
{struct model m={0};m.count=4;m.status=0x10;return m;}
int main(void)
{
    unsigned cases=0;
    struct model m=fresh();struct xcal_bus b=bus(&m);uint32_t out=0xa5a5a5a5;
    assert(xcal_read32(&b,7,&out)==0 && out==0x78563412 && m.commands==1 && m.address==0xe1);++cases;
    m=fresh();b=bus(&m);assert(xcal_write32(&b,9,0x78563412)==0 && m.words[0]==0x78563412 && m.address==0xe0);++cases;
    for(unsigned status=0;status<64;++status) {
        m=fresh();b=bus(&m);m.status=status;out=0xa5a5a5a5;
        int r=xcal_read32(&b,7,&out);
        assert(r==((status&0x26)?XCAL_BUS_ERROR:(status&0x10)?XCAL_OK:XCAL_TIMEOUT));
        assert(out==((r==0)?0x78563412:0xa5a5a5a5));
        if(r==XCAL_TIMEOUT)assert(m.polls==7 && m.writes==3);
        ++cases;
    }
    for(unsigned i=0;i<65536;++i) {
        m=fresh();b=bus(&m);m.initial=i;out=0xa5a5a5a5;
        int r=xcal_read32(&b,0,&out);
        if(i&0x800)assert(r==XCAL_BUSY && !m.writes);
        else if(i&0x36)assert(r==XCAL_DIRTY_STATUS && !m.writes);
        else assert(r==0);
        ++cases;
    }
    for(unsigned n=0;n<256;++n) {
        m=fresh();b=bus(&m);m.count=n;out=0xa5a5a5a5;
        int r=xcal_read32(&b,0,&out);
        assert(r==(n==4?XCAL_OK:XCAL_BLOCK_LENGTH));
        assert(m.fifo==(n==4?4:0)); assert(out==(n==4?0x78563412:0xa5a5a5a5));++cases;
    }
    m=fresh();b=bus(&m); b.poll_limit=0;assert(xcal_read32(&b,0,&out)==XCAL_ARGUMENT && !m.calls);++cases;
    b.poll_limit=1000001;assert(xcal_read32(&b,0,&out)==XCAL_ARGUMENT && !m.calls);++cases;
    assert(xcal_read32(NULL,0,&out)==XCAL_ARGUMENT);assert(xcal_read32(&b,0,NULL)==XCAL_ARGUMENT);cases+=2;
    struct xcal_request r={3,1,3,8,64u<<20,55u<<20,9u<<20,316160}; struct xcal_progress p;
    m=fresh();b=bus(&m);assert(xcal_program_table(&b,&r,pause500,&m,&p)==1);
    assert(p.attempted==148 && p.completed==148 && p.table_completed==144 && p.delay_completed==144 && p.phase==3);
    assert(m.regs[0]==4 && m.cmds[0]==0x0d && m.regs[1]==4 && m.words[1]==0x0f000000);
    assert(m.regs[2]==0 && m.cmds[2]==0x0d && m.regs[3]==0 && m.words[3]==0);
    for(unsigned i=0;i<144;++i){
        assert(m.regs[i+4]==i && m.addresses[i+4]==0xe0 && m.cmds[i+4]==0x1d);
        /* Independent byte-by-byte expectation from source-order table. */
        for(unsigned j=0;j<4;++j)assert(((m.words[i+4]>>(8*j))&255)==((xcal_table[i]>>(8*(3-j)))&255));
    }++cases;
    for(unsigned i=1;i<=148;++i){m=fresh();b=bus(&m);m.fails_at=i;assert(xcal_program_table(&b,&r,pause500,&m,&p)==-1);
        assert(p.attempted==i && p.completed==i-1 && m.commands==i && p.error==XCAL_BUS_ERROR);++cases;}
    for(unsigned i=1;i<=144;++i){m=fresh();b=bus(&m);m.delay_fail=i;assert(xcal_program_table(&b,&r,pause500,&m,&p)==-1);
        assert(m.commands==4+i && p.table_completed==i && p.delay_completed==i-1 && p.error==100);++cases;}
    /* Each incompatible request is rejected before any hardware callback. */
    for(unsigned i=0;i<8;++i){struct xcal_request q=r;
        switch(i){case 0:q.mode=1;break;case 1:q.confirmed_xcalibur=0;break;case 2:q.cable=6;break;case 3:q.flags=2;break;
          case 4:q.ram=128u<<20;break;case 5:q.fb++;break;case 6:q.reserved--;break;case 7:q.hidden++;break;}
        m=fresh();b=bus(&m);assert(xcal_program_table(&b,&q,pause500,&m,&p)==0 && !m.calls);++cases;}
    for(unsigned y=0;y<480;++y)for(unsigned x=0;x<720;++x)assert(!(baseline_pixel(x,y,720,480)&0xff000000));
    assert(baseline_pixel(10,100,720,480)==0xff0000 && baseline_pixel(100,100,720,480)==0x00ff00);
    assert(baseline_pixel(200,100,720,480)==0x0000ff && baseline_pixel(719,479,720,480)==0xffffff);
    assert(baseline_pixel(10,256,720,480)==0 && baseline_pixel(10,264,720,480)==0xffffff);++cases;
    printf("PASS %u protocol/profile cases plus complete 720x480 pattern bounds\n",cases);
    return 0;
}
