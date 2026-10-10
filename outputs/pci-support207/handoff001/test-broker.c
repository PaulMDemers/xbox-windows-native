/* SPDX-License-Identifier: MIT */
#include <assert.h>
#include <setjmp.h>
#include <stdio.h>
#include <string.h>
#include "broker.h"
typedef struct model {
    long owner;unsigned status,completion,reads,writes,delays,starts;
    unsigned initial_busy,complete_after,never_complete,data;
    unsigned step,interrupt_at,terminal,terminal_writes,last_action;
} model;
static model m;static jmp_buf terminal_exit;static unsigned cases;
static unsigned rd(void *,unsigned);static void wr(void *,unsigned,unsigned);
static void delay(void *);static long cas(void *,long,long);static long exchange(void *,long);
static const xb_io io={&m,rd,wr,delay,cas,exchange};
static void point(void)
{
    ++m.step;
    if(m.interrupt_at && m.step==m.interrupt_at){
        m.interrupt_at=0;m.terminal=1;
        (void)xb_terminal(&io,1);
        assert(m.owner==XB_TERMINAL);
        longjmp(terminal_exit,1); /* HAL never returns to interrupted client. */
    }
}
static unsigned rd(void *ctx,unsigned port)
{
    model *p=ctx;point();++p->reads;
    if(port==6)return p->data;
    assert(port==0);
    if(p->initial_busy){--p->initial_busy;return 0x808;}
    if(!p->starts)return p->status;
    if(p->never_complete)return 0x808;
    if(p->complete_after){--p->complete_after;return 0x808;}
    return p->completion;
}
static void wr(void *ctx,unsigned port,unsigned value)
{
    model *p=ctx;point();++p->writes;if(p->terminal)++p->terminal_writes;
    assert(port==0 || port==2 || port==4 || port==6 || port==8);
    if(port==0)assert(value==0x37);
    if(port==2){assert(value==0x0a || value==0x1a);++p->starts;}
    if(port==6)p->last_action=value;
}
static void delay(void *ctx){model *p=ctx;point();++p->delays;}
static long cas(void *ctx,long value,long expected)
{model *p=ctx;long old;point();old=p->owner;if(old==expected)p->owner=value;return old;}
static long exchange(void *ctx,long value)
{model *p=ctx;long old;point();old=p->owner;p->owner=value;return old;}
static void fresh(void){memset(&m,0,sizeof(m));m.completion=0x10;m.data=6;++cases;}
int main(void)
{
    unsigned a,c,s,n,max_step;xb_reply r;
    for(a=0;a<256;++a)for(c=0;c<256;++c){
        fresh();r=xb_read(&io,a,c);
        if((a==0x10 && c==4)||(a==0x4c && c<2)){assert(r.result==XB_OK && r.data==6 && m.starts==1);}
        else assert(r.result==XB_INVALID && !m.reads && !m.writes);
        assert(m.owner==XB_FREE);
    }
    for(s=0;s<64;++s){
        fresh();m.completion=s;r=xb_read(&io,0x10,4);
        if((s&8)||!(s&0x37))assert(r.result==XB_TIMEOUT && m.owner==XB_QUARANTINED && r.polls==XB_POLLS+1);
        else assert(r.result==xb_decode(s) && m.owner==XB_FREE);
    }
    fresh();m.status=0x800;r=xb_read(&io,0x10,4);assert(r.result==XB_BUSY && !m.writes && m.owner==XB_FREE);
    for(s=XB_ACTIVE;s<=XB_TERMINAL;++s){fresh();m.owner=s;r=xb_read(&io,0x10,4);assert(r.result==(s==XB_ACTIVE?XB_BUSY:XB_CLOSED) && !m.reads && !m.writes);}
    fresh();m.never_complete=1;r=xb_read(&io,0x10,4);assert(r.result==XB_TIMEOUT && m.owner==XB_QUARANTINED && m.writes==4);
    n=m.writes;r=xb_read(&io,0x10,4);assert(r.result==XB_CLOSED && m.writes==n);
    for(s=XB_FREE;s<=XB_QUARANTINED;++s){
        for(a=0;a<3;++a){fresh();m.owner=s;r=xb_terminal(&io,(unsigned[]){1,0x40,0x80}[a]);assert(r.result==XB_OK && m.owner==XB_TERMINAL && m.starts==1 && m.writes==5);}
        fresh();m.owner=s;m.initial_busy=XB_POLLS;r=xb_terminal(&io,1);assert(r.result==XB_BUSY && r.polls==XB_POLLS && !m.writes && m.owner==XB_TERMINAL);
        fresh();m.owner=s;m.initial_busy=XB_POLLS-1;r=xb_terminal(&io,1);assert(r.result==XB_OK && r.polls==XB_POLLS+1 && m.starts==1);
        fresh();m.owner=s;m.never_complete=1;r=xb_terminal(&io,1);assert(r.result==XB_TIMEOUT && r.polls==XB_POLLS+1 && m.starts==1);
    }
    fresh();m.owner=XB_TERMINAL;r=xb_terminal(&io,1);assert(r.result==XB_CLOSED && !m.reads && !m.writes);
    for(a=0;a<256;++a){if(a==1 || a==0x40 || a==0x80)continue;fresh();r=xb_terminal(&io,a);assert(r.result==XB_INVALID && !m.reads && !m.writes && m.owner==XB_TERMINAL);}
    /* Inject fatal entry at every callback boundary, including an active bus.
     * longjmp models the platform's noreturn/interrupt-disabled guarantee. */
    fresh();m.complete_after=3;r=xb_read(&io,0x10,4);assert(r.result==XB_OK);max_step=m.step;
    for(n=1;n<=max_step;++n){
        fresh();m.complete_after=3;m.interrupt_at=n;
        if(setjmp(terminal_exit)==0){(void)xb_read(&io,0x10,4);assert(0);}
        assert(m.owner==XB_TERMINAL && m.terminal_writes==5 && m.last_action==1);
        s=m.writes;r=xb_read(&io,0x10,4);assert(r.result==XB_CLOSED && m.writes==s);
    }
    printf("{\"passed\":true,\"cases\":%u,\"preemption_points\":%u,\"poll_bound\":%u,\"scope\":\"compiled core model; no hardware safety claim\"}\n",cases,max_step,XB_POLLS);
    return 0;
}
