/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "arena.h"
unsigned char x258_pattern(uint32_t i,uint32_t seed)
{ return (unsigned char)((i*37u+(i>>4)*19u+(i>>8)*7u)^(seed*83u)); }
void x258_action(X258Arena *a,const X258Ops *o,void *owner,
                 const X258Request *q,X258Reply *r)
{
    uint32_t i; unsigned char *p; uint64_t physical;
    unsigned char *raw=(unsigned char *)r;
    for(i=0;i<sizeof(*r);i++)raw[i]=0;
    r->version=X258_VERSION;r->status=X258_BAD;
    if(!owner || q->reserved || q->op<X258_ALLOCATE || q->op>X258_CLOSE ||
       (q->op!=X258_WRITE && q->pattern) || (q->op==X258_WRITE && (q->pattern<1 || q->pattern>2)))return;
    if(!o->passive(o->opaque)){r->status=X258_IRQL;return;}
    if(!o->enter(o->opaque)){r->status=X258_WAIT;return;}
    if(q->op==X258_ALLOCATE) {
        if(q->generation)goto done;
        if(a->attempted){r->status=X258_BUSY;goto done;}
        a->attempted=1; /* Even a failed attempt cannot be reused under this case. */
        p=o->allocate(o->opaque);
        if(!p){r->status=X258_OOM;goto done;}
        physical=o->translate(o->opaque,p);
        if((physical&4095) || physical<0x100000 || physical>0x03c00000-X258_BYTES)goto bad_translation;
        for(i=0;i<X258_BYTES;i+=4096)
            if(o->translate(o->opaque,p+i)!=physical+i)goto bad_translation;
        for(i=0;i<X258_BYTES;i++)p[i]=x258_pattern(i,0);
        o->retain_owner(o->opaque,owner);
        a->owner=owner;a->memory=p;a->generation=1;a->physical=(uint32_t)physical;
        r->status=X258_OK;goto done;
bad_translation:
        o->discard_unpublished(o->opaque,p);r->status=X258_TRANSLATION;goto done;
    }
    if(!a->memory || a->owner!=owner){r->status=X258_OWNER;goto done;}
    if(q->op==X258_CLOSE){a->closed=1;r->status=X258_OK;goto done;}
    if(q->generation!=a->generation){r->status=X258_STALE;goto done;}
    if(a->closed){r->status=X258_QUARANTINED;goto done;}
    r->status=X258_OK;
    if(q->op==X258_READ) {
        if(a->reads>=8){r->status=X258_LIMIT;goto done;}
        /* Volatile byte accesses are genuine guest CPU loads in the native bridge. */
        for(i=0;i<X258_BYTES;i++)r->data[i]=a->memory[i];
        a->reads++;
    } else if(q->op==X258_WRITE) {
        if(a->writes>=8){r->status=X258_LIMIT;goto done;}
        for(i=0;i<X258_BYTES;i++)a->memory[i]=x258_pattern(i,q->pattern);
        a->writes++;
    }
done:
    /* Do not disclose another FileObject's physical range or contents. */
    if(a->owner==owner){r->generation=a->generation;r->physical=a->physical;
        r->bytes=a->memory?X258_BYTES:0;r->closed=a->closed;r->reads=a->reads;r->writes=a->writes;}
    o->leave(o->opaque);
}
