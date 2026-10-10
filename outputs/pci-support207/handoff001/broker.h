/* SPDX-License-Identifier: MIT
 * UP-only shared HAL owner. Terminal entry requires interrupts disabled and
 * MUST NOT return to the interrupted client. No lock waits or abort strobes.
 */
#ifndef XWN_HAL_BROKER_H
#define XWN_HAL_BROKER_H
enum { XB_FREE, XB_ACTIVE, XB_QUARANTINED, XB_TERMINAL };
enum { XB_OK, XB_INVALID, XB_BUSY, XB_CLOSED, XB_PROTOCOL, XB_COLLISION, XB_TIMEOUT };
#define XB_POLLS 10000U
typedef struct xb_io {
    void *context;
    unsigned (*read)(void *,unsigned);
    void (*write)(void *,unsigned,unsigned);
    void (*delay)(void *);
    long (*cas)(void *,long,long);
    long (*exchange)(void *,long);
} xb_io;
typedef struct xb_reply { unsigned result,status,polls,data; } xb_reply;
static unsigned xb_wait(const xb_io *io,xb_reply *r,unsigned completion)
{
    unsigned n;
    for(n=0;n<XB_POLLS;++n){
        r->status=io->read(io->context,0);++r->polls;
        if(!(r->status&0x808) && (!completion || (r->status&0x37)))return 1;
        io->delay(io->context);
    }
    return 0;
}
static unsigned xb_decode(unsigned status)
{
    if(status&0x20)return XB_TIMEOUT;
    if(status&0x05)return XB_PROTOCOL;
    if(status&0x02)return XB_COLLISION;
    return (status&0x10)?XB_OK:XB_PROTOCOL;
}
static xb_reply xb_read(const xb_io *io,unsigned address,unsigned command)
{
    xb_reply r={XB_INVALID,0,0,0};long owner;
    if(!((address==0x10 && command==4)||(address==0x4c && command<2)))return r;
    owner=io->cas(io->context,XB_ACTIVE,XB_FREE);
    if(owner!=XB_FREE){r.result=owner==XB_ACTIVE?XB_BUSY:XB_CLOSED;return r;}
    r.status=io->read(io->context,0);++r.polls;
    if(r.status&0x808){r.result=XB_BUSY;goto release;}
    io->write(io->context,0,0x37);
    io->write(io->context,4,(address<<1)|1);
    io->write(io->context,8,command);
    io->write(io->context,2,0x0a);
    if(!xb_wait(io,&r,1)){
        r.result=XB_TIMEOUT;
        /* Do not abort unknown physical controller behavior. Retain quarantine. */
        io->cas(io->context,XB_QUARANTINED,XB_ACTIVE);return r;
    }
    r.result=xb_decode(r.status);
    if(r.result==XB_OK)r.data=io->read(io->context,6)&255;
    io->write(io->context,0,0x37);
release:
    /* Never reopen a terminal gate, even in a defensive unexpected return. */
    io->cas(io->context,XB_FREE,XB_ACTIVE);return r;
}
static xb_reply xb_terminal(const xb_io *io,unsigned action)
{
    xb_reply r={XB_INVALID,0,0,0};
    /* The platform wrapper has disabled interrupts on this UP machine. An
     * interrupted transfer cannot resume. No owner mutex/spinlock is acquired.
     * Reentrant terminal entry must not issue a second command. */
    if(io->exchange(io->context,XB_TERMINAL)==XB_TERMINAL){r.result=XB_CLOSED;return r;}
    if(action!=1 && action!=0x40 && action!=0x80)return r;
    if(!xb_wait(io,&r,0)){r.result=XB_BUSY;return r;}
    io->write(io->context,0,0x37);
    io->write(io->context,4,0x20);
    io->write(io->context,8,2);
    io->write(io->context,6,action);
    io->write(io->context,2,0x1a);
    if(!xb_wait(io,&r,1)){r.result=XB_TIMEOUT;return r;}
    r.result=xb_decode(r.status);
    return r; /* Only to the noreturn wrapper, which halts regardless. */
}
#endif
