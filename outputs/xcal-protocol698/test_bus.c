/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "xcal_bus.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct event { unsigned width,port,value; };
struct model { unsigned entry,status,final,length,reads,polls,fifo,nwrites,delay;
    struct event writes[16]; };
static uint8_t r8(void *v,unsigned p)
{struct model *m=v;assert(p==9 && m->fifo<4);return (uint8_t)(0x78563412u>>(8*m->fifo++));}
static uint16_t r16(void *v,unsigned p)
{
    struct model *m=v;
    if(p==6)return (uint16_t)m->length;
    assert(p==0);
    if(!m->reads++)return (uint16_t)m->entry;
    if(m->nwrites && m->writes[m->nwrites-1].port==0)return (uint16_t)m->final;
    if(m->polls==7)return (uint16_t)m->final;
    return (uint16_t)(m->polls++<m->delay?0x818:m->status);
}
static void put(struct model *m,unsigned width,unsigned p,unsigned v)
{assert(m->nwrites<16);m->writes[m->nwrites++]=(struct event){width,p,v};}
static void w8(void *v,unsigned p,uint8_t x){put(v,1,p,x);}
static void w16(void *v,unsigned p,uint16_t x){put(v,2,p,x);}
static struct model fresh(void)
{struct model m={0};m.status=0x10;m.length=4;return m;}
static struct xcal_bus bus(struct model *m)
{return (struct xcal_bus){m,r8,r16,w8,w16,7};}
static int execute(struct model *m,int read,struct xcal_trace *t,uint32_t *v)
{struct xcal_bus b=bus(m);return read?xcal_read32(&b,0,v,t):xcal_write32(&b,0,*v,t);}
static void checkwrites(struct model *m,int read,unsigned ack)
{
    struct event expected[10]={{1,4,(unsigned)(read?0xe1:0xe0)},{1,8,0}};
    unsigned n=2;
    if(!read){for(unsigned i=0;i<4;++i)expected[n++]=(struct event){1,9,(0xa5b6c7d8u>>(8*i))&255};expected[n++]=(struct event){2,6,4};}
    expected[n++]=(struct event){1,2,13};
    if(ack)expected[n++]=(struct event){2,0,ack};
    assert(n==m->nwrites);
    for(unsigned i=0;i<n;++i)assert(expected[i].width==m->writes[i].width && expected[i].port==m->writes[i].port && expected[i].value==m->writes[i].value);
}
int main(void)
{
    unsigned cases=0;struct xcal_trace t;
    for(int read=0;read<=1;++read) {
        for(unsigned s=0;s<65536;++s) {
            struct model m=fresh();m.entry=s;uint32_t v=0xa5b6c7d8;
            int result=execute(&m,read,&t,&v);
            /* Independent per-bit truth table: host/bus active dominates. */
            int busy=(s>>3&1)||(s>>11&1);
            int dirty=(s&1)||(s>>1&1)||(s>>2&1)||(s>>4&1)||(s>>5&1);
            assert(result==(busy?XCAL_BUSY:dirty?XCAL_DIRTY_STATUS:XCAL_OK));
            assert(t.entry==s);
            if(busy||dirty)assert(m.nwrites==0 && m.fifo==0 && t.polls==0 && v==0xa5b6c7d8);
            else checkwrites(&m,read,0x10);
            ++cases;
        }
        for(unsigned s=0;s<65536;++s) {
            struct model m=fresh();m.status=s;uint32_t v=0xa5b6c7d8;
            int result=execute(&m,read,&t,&v);
            int active=(s>>3&1)||(s>>11&1);
            int error=(s&1)||(s>>1&1)||(s>>2&1)||(s>>5&1);
            int complete=(s>>4)&1;
            int timeout=active||(!error&&!complete);
            assert(result==(timeout?XCAL_TIMEOUT:error?XCAL_BUS_ERROR:XCAL_OK));
            assert(t.polls==(timeout?7u:1u));
            assert(v==((read&&result==XCAL_OK)?0x78563412u:0xa5b6c7d8u));
            assert(m.fifo==((read&&result==XCAL_OK)?4u:0u));
            checkwrites(&m,read,timeout?0:(s&55));++cases;
        }
        for(unsigned s=0;s<65536;++s) {
            struct model m=fresh();m.final=s;uint32_t v=0xa5b6c7d8;
            int result=execute(&m,read,&t,&v);
            int bad=(s&1)||(s>>1&1)||(s>>2&1)||(s>>3&1)||(s>>4&1)||(s>>5&1)||(s>>11&1);
            assert(result==(bad?XCAL_FINAL_STATUS:XCAL_OK));
            assert(v==((read&&!bad)?0x78563412u:0xa5b6c7d8u));
            assert(t.final==s);checkwrites(&m,read,16);++cases;
        }
    }
    for(unsigned n=0;n<65536;++n) {
        struct model m=fresh();m.length=n;uint32_t v=0xa5b6c7d8;
        int result=execute(&m,1,&t,&v);
        assert(result==(n==4?XCAL_OK:XCAL_BLOCK_LENGTH));
        assert(m.fifo==(n==4?4u:0u) && v==(n==4?0x78563412u:0xa5b6c7d8u));++cases;
    }
    for(unsigned d=0;d<=7;++d) {
        struct model m=fresh();m.delay=d;uint32_t v=0xa5b6c7d8;
        int result=execute(&m,1,&t,&v);assert(result==(d==7?XCAL_TIMEOUT:XCAL_OK));
        checkwrites(&m,1,d==7?0:16);++cases;
    }
    {struct model m=fresh();m.status=0;m.final=0x10;uint32_t v=0xa5b6c7d8;
     assert(execute(&m,1,&t,&v)==XCAL_TIMEOUT && t.final==0x10 && !t.ack && v==0xa5b6c7d8);checkwrites(&m,1,0);++cases;}
    {struct model m=fresh();struct xcal_bus b=bus(&m);uint32_t v=0;
     b.poll_limit=0;assert(xcal_read32(&b,0,&v,&t)==XCAL_ARGUMENT);
     b.poll_limit=1000001;assert(xcal_read32(&b,0,&v,&t)==XCAL_ARGUMENT);
     assert(xcal_read32(0,0,&v,&t)==XCAL_ARGUMENT);b.poll_limit=7;
     assert(xcal_read32(&b,0,0,&t)==XCAL_ARGUMENT);
     assert(xcal_read32(&b,0,&v,0)==XCAL_ARGUMENT);
     assert(!m.reads && !m.nwrites);cases+=5;}
    printf("PASS %u exhaustive status/length and transaction cases; modeled I/O only\n",cases);
}
